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

local_authority = st.text_input('Local authority', 'Haringey')
st.write('Selection:', local_authority )

#st.title(f'Health Equity Audit of CDC in {local_authority}')

# Define the header and main text
header_text = "Welcome to the CDC Health Equity Audit"
main_text = (
    "This Streamlit app allows you to visualize results produced by the HSMA5 Health Equity Audit for CDCs."
    " Please select your modality and demographic of interest below."
)



# Display the header and main text using markdown
st.markdown(f"## {header_text}")
st.markdown(main_text)

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


#Read in data
merged_referral_file_name = f"Stage1Outputs/Merged_{modality}_{demographic}.csv"        
merged_referral_file = pd.read_csv(merged_referral_file_name, index_col=demographic)
merged_referral_file = merged_referral_file.fillna(value=0)

count_columns = merged_referral_file.iloc[:, :3]
percentage_columns = merged_referral_file.iloc[:, 3:6]


st.markdown("## Data Overview - Counts")
# Display the first 10 rows of the selected columns
st.dataframe(count_columns.head(10).astype(int))

st.markdown("## Data Overview - Percentages")
# Display the first 10 rows of the selected columns
st.dataframe(percentage_columns.head(10).astype(int))



#streamlit run HEA_Streamlit_draft.py