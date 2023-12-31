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

#Connect this to main code later
local_authority = "Haringey"

st.title(f'Health Equity Audit of CDC in {local_authority}')

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


st.markdown("# Data Overview - Counts")
# Display the first 10 rows of the selected columns
st.dataframe(count_columns.head(10).astype(int))

st.markdown("# Data Overview - Percentages")
# Display the first 10 rows of the selected columns
st.dataframe(percentage_columns.head(10).astype(int))

merged_referral_file['Population vs CDC'] = merged_referral_file[
    'Census_Count_percentage']-merged_referral_file['CDC_Count_percentage']

merged_referral_file['Baseline vs CDC'] = merged_referral_file[
    'Baseline_Count_percentage']-merged_referral_file['CDC_Count_percentage']

comparison_columns = merged_referral_file.iloc[:, 6:]

st.markdown("# Data Overview - Comparison")
# Format the DataFrame to add '%' to the values
#formatted_df = comparison_columns.head(10).astype(int).applymap(lambda x: f"{x}%")

def color_map(val):
    if val > 0:
        return f'background-color: rgba(17, 0, 255, {val / 100})'  # Blue for larger numbers
    elif val < 0:
        return f'background-color: rgba(255, 0, 0, {-val / 100})'  # Red for smaller numbers
    return ''

# Apply the heatmap coloring using the styler
styled_df = comparison_columns.head(10).style.applymap(color_map)

# Display the styled DataFrame with heatmap
st.write(styled_df)

## Making upper/lower graphs
st.markdown("# Equity Audit - Bar Charts")

## Baseline v CDC

#set up data for graph
negative_data = merged_referral_file['Baseline vs CDC'].clip(upper=0)
positive_data = merged_referral_file['Baseline vs CDC'].clip(lower=0)

fig, ax = plt.subplots()

# Plot the negative_data and positive_data as bar charts
ax.bar(merged_referral_file.index.values, negative_data, width=1, color='r', label='Less than expected')
ax.bar(merged_referral_file.index.values, positive_data, width=1, color='b', label='More than expected')

# Add a horizontal line at y=0
plt.axhline(y=0.0, color='black', linestyle='-')

# Set labels and title
plt.ylabel('Less than expected          More than expected', fontsize=10)
plt.xlabel('Age range', fontsize=10)
plt.title(f'Baseline vs CDC: Comparison of patient groups by {demographic}', fontsize=10)

# Add a legend
ax.legend()

# Display the Matplotlib figure in Streamlit
st.pyplot(fig)


## Census v CDC

#set up data for graph
negative_data = merged_referral_file['Population vs CDC'].clip(upper=0)
positive_data = merged_referral_file['Population vs CDC'].clip(lower=0)

fig, ax = plt.subplots()

# Plot the negative_data and positive_data as bar charts
ax.bar(merged_referral_file.index.values, negative_data, width=1, color='r', label='Less than expected')
ax.bar(merged_referral_file.index.values, positive_data, width=1, color='b', label='More than expected')

# Add a horizontal line at y=0
plt.axhline(y=0.0, color='black', linestyle='-')

# Set labels and title
plt.ylabel('Less than expected          More than expected', fontsize=10)
plt.xlabel('Age range', fontsize=10)
plt.title('Population vs CDC: Comparison of patient groups by age range', fontsize=10)

# Add a legend
ax.legend()

# Display the Matplotlib figure in Streamlit
st.pyplot(fig)


## Location of referral source

st.markdown("# Referral Sources - Maps")

# Create a Streamlit map
st.map()

# Create a Folium map
m = folium.Map(location=[0, 0], zoom_start=2)
st.write(m)


#streamlit run HEA_Streamlit_draft.py