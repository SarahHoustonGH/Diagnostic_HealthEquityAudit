import folium
from folium import plugins
import pandas as pd
import json
import requests
import geopandas as gpd

#this is slow and note if this is 2011 or 2021 geojson data
df2 = gpd.read_file("Data\lsoa.geojson")

IMD = pd.read_csv("Data\IMD_LSOA_Lookup.csv")

IMD = IMD.rename(columns={'LSOA11': 'LSOA11CD'})
combineddf  = df2.merge(IMD, on='LSOA11CD', how='left')

combineddf

#User adds Local authority name for mapping of LSOAs within the LA
print("Enter name of local authority")
LA = input()

# Uses centre of chosen local authority to centre map 
# Location of centroids from  https://nihr.opendatasoft.com/explore/dataset/local_authority_districts/table/
location_data = pd.read_csv("Data\LA_locations.csv")
LA_location = location_data[location_data['LAD23NMW'].str.startswith(LA)]
LA_location_lat= LA_location[["LAT"]].values
LA_location_long= LA_location[["LONG"]].values


# Create base map
imd_map = folium.Map(location=[LA_location_lat,LA_location_long],
                        zoom_start=12,
                        tiles='cartodbpositron')

imd_map


#Return all LSOA names with a substring of the LA name
df3 = combineddf[combineddf['LSOA11NM'].str.startswith(LA)]
print(df3)

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
                  highlight=True).add_to(imd_map)

imd_map

#Read in the GP location data to be displayed on the LSOA map
df_gp =  pd.read_csv("Stage1Outputs\GPSummaryReferralData_U_Map.csv")

for (index, row) in df_gp.iterrows():
    pop_up_text = f"The postcode for {row.loc['GP practice name']} " #+ \
                     #is {row.loc['Postcode']}"
    folium.Circle(location=[row.loc['Latitude'], row.loc['Longitude']],
                  #radius=1000,  # Adjust the radius as needed,
                  radius = row.loc["CountReferrals_Baseline"],
                  fill = True,
                  fill_opacity = 0.9,
                  color = 'black',
                  popup=pop_up_text, 
                  tooltip=f"{row.loc['GP practice name']} sent {row.loc['CountReferrals_Baseline']} referrals").add_to(imd_map)
    
