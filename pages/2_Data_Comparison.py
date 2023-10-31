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

#Create buttons in sidebar

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
    ["age", "gender", "ethnicity","GP_IMD", "Pop_IMD"])

merged_referral_file_name = f"Stage1Outputs/Merged_{modality}_{demographic}.csv"        
merged_referral_file = pd.read_csv(merged_referral_file_name, index_col=demographic)
merged_referral_file = merged_referral_file.fillna(value=0)

st.markdown("## Data Comparison")

st.markdown(
    "This Streamlit app allows you to visualize results produced by the HSMA5 Health Equity Audit for CDCs."
    "  :point_left: Please select your modality and demographic of interest in the panel on the left."
)

#Displaying summary of referrals
st.subheader('Summary of referrals', divider='grey')

#Read in data
count_columns = merged_referral_file.iloc[:, :3]
percentage_columns = merged_referral_file.iloc[:, 3:6]

#Set columns
col1, col2 = st.columns(2)

# Display the first 10 rows of the selected columns
col1.subheader('Count of referrals')
col1.dataframe(count_columns.head(10).astype(int))

# Display the first 10 rows of the selected columns
col2.subheader('Percentage of referrals')
percentage_columns = percentage_columns.head(10).astype(float)
formatted_df = percentage_columns.applymap(lambda x: f"{x:.1f}%")
col2.dataframe(formatted_df)



#Population set as location of column as the names differ between IMD and other modalities
merged_referral_file['Population vs CDC'] = merged_referral_file.iloc[:,4]-merged_referral_file['CDC_Count_percentage']

merged_referral_file['Baseline vs CDC'] = merged_referral_file[
    'Baseline_Count_percentage']-merged_referral_file['CDC_Count_percentage']

comparison_columns = merged_referral_file.iloc[:, 6:]

st.subheader('Equity Audit', divider='grey')

st.markdown("### Data Overview")

# Read the value from the file or database
with open("Stage1Outputs/user_local_authority.txt", "r") as f:
    local_authority = f.read()

st.markdown(f"The local authority selected at processing stage was: **{local_authority}**")

st.markdown("The table below displays the propertional difference in referrals from population group. "
            "An increase in referrals from the comparator group (e.g. Population or baseline) appear as blue. "
            "A decrease in referrals appears as red.")
# Format the DataFrame to add '%' to the values
#formatted_df = comparison_columns.head(10).astype(int).applymap(lambda x: f"{x}%")

def color_map(val):
    if val > 0:
        return f'background-color: rgba(17, 0, 255, {val / 100})'  # Blue for larger numbers
    elif val < 0:
        return f'background-color: rgba(255, 0, 0, {-val / 100})'  # Red for smaller numbers
    return ''

# Apply the heatmap coloring using the styler
styled_df = comparison_columns.head(10).style.applymap(color_map).format('{:.1f}')

# Display the styled DataFrame with heatmap
#st.write(styled_df)
st.dataframe(data=styled_df, use_container_width=True)

st.markdown("SPACE FOR INTERPRETATION AND DATA STRATEGY SENTENCES")

## Making upper/lower graphs
st.markdown("### Bar Charts")

st.markdown("The graph also displays the proportional difference in referrals. "
            "An increase in referrals from the comparator group (e.g. Population or baseline) appear as blue. "
            "A decrease in referrals appears as red.")

#Set columns
col1, col2 = st.columns(2)

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
plt.xlabel(f'{demographic}', fontsize=10)
plt.title(f'Baseline vs CDC: Comparison of patient groups by {demographic}', fontsize=10)

# Add a legend
ax.legend()

# Display the Matplotlib figure in Streamlit
col1.pyplot(fig)


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
plt.xlabel(f'{demographic}', fontsize=10)
plt.title(f'Population vs CDC: Comparison of patient groups by {demographic}', fontsize=10)

# Add a legend
ax.legend()

# Display the Matplotlib figure in Streamlit
col2.pyplot(fig)
