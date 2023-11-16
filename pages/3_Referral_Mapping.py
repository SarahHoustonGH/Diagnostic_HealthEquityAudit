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

### Mapping ------------------------------------------------

st.markdown("## Referral Mapping")


st.markdown(
    "This Streamlit app allows you to visualize results produced by the HSMA5 Health Equity Audit for CDCs."
    "  :point_left: Please select your modality of interest in the panel on the left."
)

#Create buttons in sidebar

with st.sidebar:
    add_radio = modality = st.radio(
    "What modality would you like to view?",
    ["X", "U"],
    captions = ["X ray", "Ultrasound"])

# Read the value from the file or database
with open("Stage1Outputs/user_local_authority.txt", "r") as f:
    local_authority = f.read()

st.markdown(f"The local authority selected at processing stage was: **{local_authority}**")

#local_authority = st.text_input('Local authority', 'Haringey')
#st.write('Selection:', local_authority )

st.subheader('Source of GP referrals', divider='grey')

st.markdown("The map below displays the GP practice and number of referrals sent from each practice"
            " during the time period selected.")

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
                        zoom_start=12,
                        tiles='cartodbpositron')



#Return all LSOA names with a substring of the LA name
df3 = combineddf[combineddf['LSOA11NM'].str.startswith(LA)]

#Read in the data to be displayed on the LSOA map
df_lsoa_imd =  pd.read_csv(f"Stage2Outputs\GPSummaryReferralData_{modality}_Map.csv")

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


#Read in the GP location data to be displayed on the LSOA map
#df_gp =  pd.read_csv(f"Stage1Outputs\GPSummaryReferralData_{modality}_Map.csv")

for (index, row) in df_lsoa_imd.iterrows():
    pop_up_text = f"The postcode for {row.loc['GP practice name']} " #+ \
                     #is {row.loc['Postcode']}"
    folium.Circle(location=[row.loc['Latitude'], row.loc['Longitude']],
                  #radius=1000,  # Adjust the radius as needed,
                  radius = row.loc["Count_Referrals_CDC"],
                  fill = True,
                  fill_opacity = 0.9,
                  color = 'black',
                  popup=pop_up_text, 
                  tooltip=f"{row.loc['GP practice name']} sent {row.loc['Count_Referrals_CDC']} referrals").add_to(m)
    
folium_static(m)


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


st.subheader('Identifying missing practices', divider='grey')

st.markdown("The map below displays the GP practice and whether a referral was received from that practice"
            " during the time period selected.")

m2 = folium.Map(location=[LA_location_lat,LA_location_long],
                        zoom_start=12,
                        tiles='cartodbpositron')

folium.Choropleth(
                geo_data = df3,      
                  data=df3,
                  columns=['LSOA11CD', 'IMD2019 Decile'],
                  key_on="properties.LSOA11CD",
                  fill_color ='YlGnBu',      
                  fill_opacity = 0.5,
                  legend_name='IMD',
                  highlight=True).add_to(m2)

# Read in all GP data for region
allGPdata =  pd.read_csv(f"Stage2Outputs\GP_location_data.csv")
df_lsoa_imd = df_lsoa_imd.rename(columns={'Patient GP': 'CODE'})
practicereferralmap  = allGPdata.merge(df_lsoa_imd, on='CODE', how='left')
practicereferralmap = practicereferralmap.fillna(0)


for (index, row) in practicereferralmap.iterrows():
    pop_up_text = f"The postcode for {row.loc['GP practice name']} " + \
                     "is {row.loc['Postcode']}"
    color = 'red' if row.loc["Count_Referrals_CDC"] == 0 else 'black'
    folium.Circle(location=[row.loc['Latitude_x'], row.loc['Longitude_x']],
                  #radius=1000,  # Adjust the radius as needed,
                  fill = True,
                  fill_opacity = 0.9,
                  color = color,
                  popup=pop_up_text, 
                  tooltip=f"{row.loc['CODE']} sent {row.loc['Count_Referrals_CDC']} referrals").add_to(m2)
    
folium_static(m2)

st.subheader('Source of referrals by LSOA', divider='grey')

st.markdown("The map below displays the LSOAs from which referrals to the CDC were received for this modality."
            " ")

m3 = folium.Map(location=[LA_location_lat,LA_location_long],
                        zoom_start=12,
                        tiles='cartodbpositron')

combineddf = combineddf.rename(columns={'LSOA11CD': 'LSOA11'})
combineddf2  = combineddf.merge(practicereferralmap, on='LSOA11', how='left')

df4 = combineddf2[combineddf2['LSOA11NM'].str.startswith(LA)]

pop_up_text2 = f"{row.loc['GP practice name']} " + \
                f"sent {row.loc['Count_Referrals_CDC']} referrals"

folium.Choropleth(
                geo_data = df4,      
                  data=df4,
                  columns=['LSOA11', 'Count_Referrals_CDC'],
                  key_on="properties.LSOA11",
                  fill_color ='Purples',      
                  fill_opacity = 0.5,
                  legend_name='Count of Referrals',
                  popup=pop_up_text2, 
                  highlight=True).add_to(m3)

folium_static(m3)