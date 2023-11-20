import streamlit as st
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import geopandas as gpd
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster
from folium import plugins
import pandas as pd
import json
import requests
import geopandas as gpd
import streamlit_folium
from streamlit_folium import st_folium
from streamlit_folium import folium_static

st.set_page_config(
    page_title="CDC Health Equity Audit"
)


#st.title(f'Health Equity Audit of CDC in {local_authority}')

# Define the header and main text
header_text = "Welcome to the Automated CDC Health Equity Audit"
main_text = (
    "This Streamlit app allows you to visualize results produced by the HSMA5 Automated Health Equity Audit for CDCs."
)



# Display the header and main text using markdown
st.markdown(f"## {header_text}")
st.markdown(main_text)

## Removed LA input as not possible in current data flow - Selection takes
## place at Python stage

#local_authority = st.text_input('Local authority', 'Haringey')
#st.write('Selection:', local_authority )

# Read the value from the file or database
with open("Stage1Outputs/user_local_authority.txt", "r") as f:
    local_authority = f.read()

st.markdown(f"The local authority selected at processing stage was: **{local_authority}**")


# Create a Folium map
#this is slow and note if this is 2011 or 2021 geojson data
 
df2 = gpd.read_file("Data\lsoa.geojson")

IMD = pd.read_csv("Data\IMD_LSOA_Lookup.csv")

IMD = IMD.rename(columns={'LSOA11': 'LSOA11CD'})
combineddf  = df2.merge(IMD, on='LSOA11CD', how='left')


#User adds Local authority name for mapping of LSOAs within the LA
#print("Enter name of local authority")
LA = local_authority

# Uses centre of chosen local authority to centre map 
# Location of centroids from  https://nihr.opendatasoft.com/explore/dataset/local_authority_districts/table/
location_data = pd.read_csv("Data\LA_locations.csv")
LA_location = location_data[location_data['LAD23NMW'].str.startswith(LA)]
LA_location_lat= LA_location[["LAT"]].values
LA_location_long= LA_location[["LONG"]].values


# Create base map
m = folium.Map(location=[LA_location_lat,LA_location_long],
                        zoom_start=10,
                        tiles='cartodbpositron')



#Return all LSOA names with a substring of the LA name
df3 = combineddf[combineddf['LSOA11NM'].str.startswith(LA)]

#Read in the data to be displayed on the LSOA map
df_lsoa_imd =  pd.read_csv("Stage2Outputs\GPSummaryReferralData_U_Map.csv")

#df2["LSOA21CDtxt"] = df2["LSOA21CD"].astype(str)
folium.Choropleth(
                geo_data = df3,      
                  data=df3,
                  columns=['LSOA11CD', 'IMD2019 Decile'],
                  key_on="properties.LSOA11CD",
                  fill_color ='YlGnBu',      
                  fill_opacity = 0.5,
                  legend_name='IMD',
                  highlight=True).add_to(m)

# Custom CSS to adjust the map size
st.write(
    f"""
    <style>
        .map-container {{
            width: 80vw;
            height: 40vh;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)



#Sum of population for display
pop_data = pd.read_csv(f"Stage1Outputs\Census_ethnicity_summary_{local_authority}.csv")
sum_of_pop = pop_data['OBS_VALUE'].sum()

#Proportion of patients at GP practices in Core20
filtered_core20 = df_lsoa_imd[df_lsoa_imd['IMD2019 Decile'] <= 2]
prop_of_Core20 = (filtered_core20["NUMBER_OF_PATIENTS"].sum()/df_lsoa_imd["NUMBER_OF_PATIENTS"].sum()) * 100

#Display text to describe the region
st.subheader('Summary of region', divider='grey')
st.markdown(f"In the 2021 Census, {local_authority} had a population of {sum_of_pop}. "
    f"{prop_of_Core20:.1f}% of patients registered to a GP in {local_authority} were registered "
    "with a practice in the Core20 (IMD 1 + 2). The map below displays the LSOAs coloured "
    "by their respective Index of Multiple Deprivation decile (1 being most deprived, 10 being least deprived).")

postcode = st.text_input(f'Add the postcode of your CDC in {local_authority} to display on the map (e.g., SW1A 1AA):')

def get_coordinates(postcode):
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(postcode)
    if location:
        return location.latitude, location.longitude
    return None

#Display postcode on map
if postcode:
    # Get coordinates from the postcode
    coordinates = get_coordinates(postcode)
    if coordinates:
            # Add marker
            folium.Marker(
                location=coordinates,
                popup='CDC',
                icon=folium.Icon(color='black')
           ).add_to(m)
    else:
            st.error('Invalid postcode or location not found.')

# Display the Folium map
folium_static(m)

# st.subheader('IMD summary', divider='grey')

