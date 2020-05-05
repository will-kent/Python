import streamlit as st
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
origin_colour = [21,65,204]
dest_colour = [230,25,31]
covid_colour = [134,11,0,200]
highlight_colour = [91,221,34]


@st.cache
def load_csv_data(src, dates):
    data = pd.read_csv(src)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    for date in dates:
        data[date] = pd.to_datetime(data[date])
    return data

# Variable for date picker, default to Jan 1st 2020
start_date = datetime.date(2020,1,1)

# Load Data
flight_data = load_csv_data(flight_data_path, flight_data_dates)
covid_data = load_csv_data(covid_data_path, [])
covid_data["date"] = pd.to_datetime(covid_data["date"], format = "%d/%m/%Y")

# Set sidebar options
select_covid_list = []
covid_index = [4,5,6,7,8,9,10,11,12,13,14,15]
covid_measures = np.array(list(covid_data))[covid_index]
for measure in covid_measures:
    measure_name = measure.replace("_"," ")
    select_covid_list.append(measure_name)

# Set viewport for the deckgl map
view = pdk.ViewState(latitude=0, longitude=40, zoom=0.4)

# Create sidebar options
origin_choice = st.sidebar.multiselect(
    'Select the origin of the country',
    flight_data.groupby('origin_country').count().reset_index()['origin_country'].tolist()
    )

dest_choice = st.sidebar.multiselect(
    'Select the destination of the country',
    flight_data.groupby('destination_country').count().reset_index()['destination_country'].tolist()
    )

covid_measure = st.sidebar.radio("Select a COVID-19 measure to display", select_covid_list)
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
        radius_scale=5,
        radius_min_pixels=1,
        radius_max_pixels=1000,
        line_width_min_pixels=1,
        get_position=["longitude", "latitude"],
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

# Create a subheading to display current date
chart_date = date.strftime('%d %m %Y')
chart_subheader = st.subheader(chart_date)

# Create the deck.gl map
r = pdk.Deck(
    layers=[covid_layer,flight_layer],
    initial_view_state=view,
    map_style="mapbox://styles/mapbox/dark-v9",
    #map_style = "https://s3.amazonaws.com/cdn.brianbancroft.io/assets/osmstyle.json",
    tooltip=tooltip_value
)

# Render the map to make it avialable to all
map = st.pydeck_chart(r)

# Update the maps and the subheading each day for 90 days
for i in range(0, 90, 1):
    # Increment day by 1
    date += datetime.timedelta(days=1)

    # Update data in map layers
    flight_layer.data = flight_subset[flight_subset['firstseen'].dt.normalize() == date.isoformat()]
    covid_layer.data = covid_data[covid_data['date'] == date.isoformat()]
    # Update the deck.gl map
    r.update()

    # Render the map
    map.pydeck_chart(r)

    # Update the heading with current date
    chart_date = date.strftime('%d %m %Y')
    chart_subheader.subheader(chart_date)

    # wait 0.1 second before go onto next day
    time.sleep(0.1)