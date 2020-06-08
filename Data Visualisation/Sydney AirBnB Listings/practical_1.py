import streamlit as st
import pandas as pd
import altair as alt

data_path = "listings_syd_Mar2020.csv"
date_columns = ["last_review"]

@st.cache
def load_csv_data(src, dates):
    data = pd.read_csv(src)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    for date in dates:
        data[date] = pd.to_datetime(data[date])
    return data

# Load Data
data = load_csv_data(data_path, date_columns)

#st.header("Data Loaded")
#st.write(data)
st.title("March 2020 AirBnB Listings in Sydney")
st.write("This page allows you to explore Sydney AirBnB listings for March 2020. Please use the filters on the left to explore the data.")

# Create filters
room_type_choice = st.sidebar.multiselect(
    'Room Type',
    data.groupby('room_type').count().reset_index()['room_type'].tolist()
    )

neighbourhood_choice = st.sidebar.multiselect(
    'Neighbourhood',
    data.groupby('neighbourhood').count().reset_index()['neighbourhood'].tolist()
    )

price_slider = st.sidebar.slider('Select Price Range',
                                                   int(data['price'].min()),
                                                   int(data['price'].max()),
                                                   (int(data['price'].min()), int(data['price'].max()))
                                                   )

# Create data subset and apply selected filters
subset = data

if len(room_type_choice) > 0:
    subset = subset[subset['room_type'].isin(room_type_choice)]
    
if len(neighbourhood_choice) > 0:
    subset = subset[subset['neighbourhood'].isin(neighbourhood_choice)]
    
subset = subset[subset['price'].between(price_slider[0], price_slider[1])]

# Create map showing location of AirBnB listings in March 2020
st.header("2.1 March 2020 Sydney AirBnB Listings")
src_json = "https://raw.githubusercontent.com/will-kent/Python/master/Data%20Visualisation/Sydney%20AirBnB%20Listings/sydney_LGAs.json"
source = alt.topo_feature(src_json, 'sydney_LGAs')

# Create map layer
baseMap = alt.Chart(source).mark_geoshape(
    fill = "#C7C7C7",
    stroke = "white"
).properties(
    width = 800,
    height = 600
).project("mercator")

# Create location marks on map
points = alt.Chart(subset).mark_circle(color = "#1CA4F3", opacity = 0.5).encode(
    longitude = 'longitude:Q',
    latitude = 'latitude:Q',
    tooltip = [alt.Tooltip('name:N', title = "Property Name"),
               alt.Tooltip('room_type:N', title = "Room Type"),
               alt.Tooltip('price:Q', title = "Price"),
               alt.Tooltip('neighbourhood:N', title = "Neighbourhood")
               ]
    )
    
st.altair_chart(baseMap+points)

# Create bar chart showing number of listings per neighbour
st.header("2.2 March 2020 Total Number of Listings by Neighbourhood")

barChart = alt.Chart(subset).mark_bar(color = "#1CA4F3").encode(
    x = alt.X('count(id):Q',  title='Number of Airbnbs'),
    y = alt.Y('neighbourhood:N', type='nominal', sort='-x', title='Neighbourhood'),
    tooltip = [alt.Tooltip('neighbourhood:N', title = "Neighbourhood"),
               alt.Tooltip('count(id):Q', title = "Number of properties")
               ]
).properties(
    width = 800,
    height = 600
)

st.altair_chart(barChart)