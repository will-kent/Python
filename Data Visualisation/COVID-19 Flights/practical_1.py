import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import pydeck as pdk
import datetime
import time

# Data sources
# Flights to and from Australian between Jan and March 2020 from https://zenodo.org/record/3737102
flight_data_path = "flights-jan-mar-2020.csv" 
flight_data_dates = ["firstseen","lastseen"]

# COVID-19 data from https://ourworldindata.org/coronavirus
covid_data_path = "covid.csv"
covid_data_date = ["date"]

# Set start date of animation
date = datetime.date(2020,1,1)

# Set colours
origin_colour = [80,217,84,80]
dest_colour = [217,84,80,80]
covid_colour = [134,11,0,200]
highlight_colour = [84,80,217,255]

# Variable for date picker, default to Jan 1st 2020
start_date = datetime.date(2020,1,1)

# Load Data
flight_data = pd.read_csv(flight_data_path)
covid_data = pd.read_csv(covid_data_path)

# Make dates, dates again
flight_data["firstseen"] = pd.to_datetime(flight_data["firstseen"])
flight_data["lastseen"] = pd.to_datetime(flight_data["lastseen"])
covid_data["date"] = pd.to_datetime(covid_data["date"], format = "%d/%m/%Y")

# Set sidebar options
select_covid_list = []
covid_index = [4,5,6,7,8,9,10,11,12,13,14,15]
covid_measures = np.array(list(covid_data))[covid_index]
for measure in covid_measures:
    measure_name = measure.replace("_"," ")
    select_covid_list.append(measure_name)

# Set viewport for the deckgl map
view = pdk.ViewState(latitude=0, longitude=15, zoom=0.4)

# Create sidebar options
st.sidebar.markdown("Select parameters and press \"Play\"")
animate = st.sidebar.button("Play")

origin_choice = st.sidebar.multiselect(
    'Select the origin of the country',
    flight_data.groupby('origin_country').count().reset_index()['origin_country'].tolist()
    )

dest_choice = st.sidebar.multiselect(
    'Select the destination of the country',
    flight_data.groupby('destination_country').count().reset_index()['destination_country'].tolist()
    )

covid_measure = st.sidebar.radio("Select a COVID-19 measure to display", select_covid_list)
covid_measure_nice_name = covid_measure
covid_measure = covid_measure.replace(" ","_")

# Create subset of flight data based on selections made
flight_subset = flight_data

if len(origin_choice) > 0:
    flight_subset = flight_subset[flight_subset['origin_country'].isin(origin_choice)]
    
if len(dest_choice) > 0:
    flight_subset = flight_subset[flight_subset['destination_country'].isin(dest_choice)]

 
# Create the arc layer
flight_layer = pdk.Layer(
    "ArcLayer",
    data=flight_subset,
    get_width=2,
    get_source_position=['origin_lng', 'origin_lat'],
    get_target_position=['destination_lng', 'destination_lat'],
    get_source_color=origin_colour,
    get_target_color=dest_colour,
    pickable=True,
    auto_highlight=True,
    highlight_color=highlight_colour,
    )

# Create the scatter plot layer
covid_layer = pdk.Layer(
        "ScatterplotLayer",
        data=covid_data,
        pickable=False,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=5, # 5
        radius_min_pixels=1,
        radius_max_pixels=30, # 1000
        line_width_min_pixels=1,
        get_position=["Longitude", "Latitude"],
        get_radius=covid_measure,
        get_fill_color=covid_colour,
        get_line_color=covid_colour,
    )

# Configure the tooltip
tooltip_value = {"html": "Flight {number} from {origin_country} to {destination_country}",
        'style': {
            'color': 'white',
            'background': 'black'}
        }

# Create the deck.gl map
r = pdk.Deck(
    layers=[covid_layer,flight_layer],
    initial_view_state=view,
    map_style="mapbox://styles/mapbox/dark-v9",
    #map_style = "https://s3.amazonaws.com/cdn.brianbancroft.io/assets/osmstyle.json",
    tooltip=tooltip_value
)

# Create Covid chart
# Trim covid data frame to period interested in
covid_subset = covid_data[covid_data["date"] <= datetime.datetime(2020, 3, 31)]

# Get maximum value for selected covid "measure" - required for line chart
max_value = covid_subset.groupby("date")[covid_measure].sum().max()

# Bar chart of "measure" by Country - Didin't look that great
#covid_cases_chart = alt.Chart(covid_subset).transform_aggregate(
#    max_value = "max(" + covid_measure + ")", groupby = ["Country"]
#).transform_window(
#    rank = "rank(max_value)",
#    frame = [None, 0],
#    sort = [alt.SortField("max_value", order = "descending")]
#).transform_filter(
#    alt.datum.rank <= 10
#).mark_bar(color = "#212aba").encode(
#    x = alt.X("max_value:Q",  title = covid_measure.replace("_"," ")),
#    y = alt.Y("Country:N", type = "nominal", sort = "-x", title = "Country"),
#    tooltip = [alt.Tooltip("max_value:Q", title = covid_measure.replace("_"," "))]
#    ).properties(
#        width = 700,
#        height = 500
#        )

covid_cases_chart = alt.Chart(covid_subset).transform_aggregate(
    sum_value = "sum(" + covid_measure + ")", groupby = ["date"]
    ).mark_line(color = "#212aba").encode(
    x = alt.X("date", title = "", scale = alt.Scale(
        domain = [datetime.datetime(2020, 1, 1).isoformat(), datetime.datetime(2020, 3, 31).isoformat()])),
    y = alt.Y("sum_value:Q", title = covid_measure_nice_name, scale = alt.Scale(
        domain = [0, max_value]))
    ).properties(
        width = 700,
        height = 500
        )

# Create a subheading to display current date
page_header = st.header("COVID-19 and Global Travel")
st.write("Australia is a nation of travellers but COVID-19 has delayed many a journey. How have flights into, and out of, Australia and ", \
         "New Zealand been impacted as the COVID-19 pandemic has spread?")
st.write("Use the options to the left to investigate the spread of COVID-19 and its impact on Global Travel. Press \"Play\" to watch the ", \
         "evolution of the pandemic and its imapct.")

chart_date = date.strftime('%d %m %Y')
chart_subheader = st.subheader("Flights and COVID-19 " + covid_measure_nice_name +" on " + chart_date)

# Render the map to make it avialable to all
map = st.pydeck_chart(r)

st.write("")

# Render the bar chart of COVID-19 Values
covid_line_subheader = st.subheader("The number of COVID-19 " + covid_measure_nice_name + " on " + chart_date)
covid_line = st.altair_chart(covid_cases_chart)

# Update the maps and the subheading each day for 90 days
if animate:
    for i in range(0, 90, 1):
        # Increment day by 1
        date += datetime.timedelta(days=1)
    
        # Update data in map layers
        flight_layer.data = flight_subset[flight_subset['firstseen'].dt.normalize() == date.isoformat()]
        covid_layer.data = covid_data[covid_data['date'] == date.isoformat()]
        covid_cases_chart.data = covid_data[covid_data['date'] <= date.isoformat()]
        
        # Update the deck.gl map
        r.update()
    
        # Render the map
        map.pydeck_chart(r)
        covid_line.altair_chart(covid_cases_chart)
    
        # Update the heading with current date
        chart_date = date.strftime('%d %m %Y')
        chart_subheader.subheader("Flights and COVID-19 " + covid_measure_nice_name +" on " + chart_date)
        covid_line_subheader.subheader("The number of COVID-19 " + covid_measure_nice_name + " on " + chart_date)
    
        # wait 0.1 second before go onto next day
        time.sleep(0.2)