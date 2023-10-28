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

st.set_page_config(
    page_title="CDC Health Equity Audit"
)



#st.title(f'Health Equity Audit of CDC in {local_authority}')

# Define the header and main text
header_text = "Welcome to the CDC Health Equity Audit"
main_text = (
    "This Streamlit app allows you to visualize results produced by the HSMA5 Health Equity Audit for CDCs."
    "  :point_left: Please select your modality and demographic of interest in the panel on the left."
)



# Display the header and main text using markdown
st.markdown(f"## {header_text}")
st.markdown(main_text)

local_authority = st.text_input('Local authority', 'Haringey')
st.write('Selection:', local_authority )

#Create buttons in sidebar
with st.sidebar:
    st.markdown("# CDC Health Equity Audit")

with st.sidebar:
    st.markdown("## Options")

with st.sidebar:
    add_radio = modality = st.radio(
    "What modality would you like to view?",
    ["X", "U"],
    captions = ["X ray", "Ultrasound"])

with st.sidebar:
    add_radio = demographic = st.radio(
    "What demographic would you like to disaggregate by?",
    ["age", "gender", "ethnicity"])



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
df_lsoa_imd =  pd.read_csv("Stage1Outputs\GPSummaryReferralData_U_Map.csv")

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

st_data = st_folium(m)

#Read in data
merged_referral_file_name = f"Stage1Outputs/Merged_{modality}_{demographic}.csv"        
merged_referral_file = pd.read_csv(merged_referral_file_name, index_col=demographic)
merged_referral_file = merged_referral_file.fillna(value=0)

count_columns = merged_referral_file.iloc[:, :3]
percentage_columns = merged_referral_file.iloc[:, 3:6]

#Set columns
col1, col2 = st.columns(2)


st.markdown("## Data Overview - Counts")
# Display the first 10 rows of the selected columns
col1.dataframe(count_columns.head(10).astype(int))

st.markdown("## Data Overview - Percentages")
# Display the first 10 rows of the selected columns
col2.dataframe(percentage_columns.head(10).astype(int))



#streamlit run HEA_Streamlit_draft.py