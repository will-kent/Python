import streamlit as st
import pandas as pd

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

st.header("Data Loaded")
st.write(data)

# Create filters
room_type_choice = st.sidebar.multiselect(
    'Room Type',
    data.groupby('room_type').count().reset_index()['room_type'].tolist()
    )

neighbourhood_choice = st.sidebar.multiselect(
    'Neighbourhood',
    data.groupby('neighbourhood').count().reset_index()['neighbourhood'].tolist()
    )

min_price_slider = st.sidebar.slider('The minimum price per night', int(data['price'].min()), int(data['price'].max()), int(data['price'].mean()))

# Create data subset and apply selected filters
subset = data

if len(room_type_choice) > 0:
    subset = data[data['room_type'].isin(room_type_choice)]
    
if len(neighbourhood_choice) > 0:
    subset = data[data['neighbourhood'].isin(neighbourhood_choice)]
    
subset = subset[subset['price'] >= min_price_slider]

st.subheader("Map")


st.subheader("Bar Chart")
