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
from matplotlib.ticker import FuncFormatter

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

merged_referral_file_name = f"Stage2Outputs/Merged_{modality}_{demographic}.csv"        
merged_referral_file = pd.read_csv(merged_referral_file_name, index_col=demographic)
merged_referral_file = merged_referral_file.fillna(value=0)

st.markdown("## Data Comparison")

st.markdown(
    "This Streamlit app allows you to visualize results produced by the HSMA5 Health Equity Audit for CDCs."
    "  :point_left: Please select your modality and demographic of interest in the panel on the left."
)

### Data summary analysis

#Read in data
count_columns = merged_referral_file.iloc[:, :3]
percentage_columns = merged_referral_file.iloc[:, 3:6]

percentage_columns = percentage_columns.head(10).astype(float)
ct_formatted_df = percentage_columns.applymap(lambda x: f"{x:.1f}%")


#Population set as location of column as the names differ between IMD and other modalities
merged_referral_file['Baseline vs Population'] = merged_referral_file['Baseline_Count_percentage']-merged_referral_file.iloc[:,3]

merged_referral_file['CDC vs Baseline'] = merged_referral_file['CDC_Count_percentage']-merged_referral_file['Baseline_Count_percentage']

merged_referral_file['CDC vs Population'] = merged_referral_file['CDC_Count_percentage']-merged_referral_file.iloc[:,3]

# Add % sign to columns
columns_to_format = ['Baseline vs Population', 'CDC vs Baseline', 'CDC vs Population']

comparison_columns = merged_referral_file.iloc[:, 6:]

st.subheader('Equity Audit', divider='grey')

st.markdown("#### Data Overview")

# Read the value from the file or database
with open("Stage1Outputs/user_local_authority.txt", "r") as f:
    local_authority = f.read()

st.markdown(f"The local authority selected at processing stage was: **{local_authority}**")

st.markdown("The table below displays the proportional difference of referrals to a comparator group. "
            "An increase in referrals from the comparator group (e.g. Population or baseline) appear as blue. "
            "A decrease in referrals appears as red.")
# Format the DataFrame to add '%' to the values
#formatted_df = comparison_columns.head(10).astype(int).applymap(lambda x: f"{x}%")

def color_map(val):
    if val > 0:
        return f'background-color: rgba(0, 0, 255, {val / 100})'  # Stronger Blue for larger numbers
    elif val < 0:
        return f'background-color: rgba(255, 0, 0, {-val / 100})'  # Stronger Red for smaller numbers
    return ''

# Apply formatting to the DataFrame (numeric formatting)
formatted_df = comparison_columns.head(10).style.format('{:.1f}%')

# Apply the color map using the apply() function with a lambda function
styled_df = formatted_df.apply(lambda x: x.apply(color_map))

# Set values to be centrally aligned
styled_df = styled_df.set_properties(**{'text-align': 'center'})

# Display the styled DataFrame with heatmap
st.dataframe(data=styled_df, use_container_width=True)


## Data Strategy

ethnicity_info = "Collection of ethnicity is essential in mapping health inequity. Please see the below links for more details on the importance of ethnicity recording and how to address issues of data quality."

# Check if "Unknown" index exists in percentage_columns DataFrame
if "Unknown" in percentage_columns.index:
    # If "Unknown" exists, fetch the value
    cdc_unknown_percentage = percentage_columns.loc["Unknown", "CDC_Count_percentage"]
    formatted_cdc_percentage = f"{cdc_unknown_percentage:.1f}%"

    # Display the sentence with the formatted percentage
    st.markdown("#### Highlighting incomplete data")
    st.markdown(f"{formatted_cdc_percentage} of your CDC referrals do not have a usable {demographic} recorded. "
                "This should be considered in your interpretation of results.")

# Display links
    # Check for demographic and display additional information if it's "ethnicity"
    if demographic == "ethnicity":
        st.markdown(ethnicity_info)
        st.markdown("""
                    -	[Standards for ethnicity data, GOV.UK](https://www.gov.uk/government/consultations/standards-for-ethnicity-data/standards-for-ethnicity-data)
                    -	[How do we collect good-quality data on race and ethnicity and address the trust gap? (Mathur et al, 2022)](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(22)02490-4/fulltext)
                    -	[Recording ethnicity in primary care: assessing the methods and impact (Hull et al, 2011)](https://bjgp.org/content/61/586/e290)                
                    -	[Measuring equality: A guide for the collection and classification of ethnic group, national identity and religion data in the UK. (ONS, 2021)](https://www.ons.gov.uk/methodology/classificationsandstandards/measuringequality/ethnicgroupnationalidentityandreligion)
                    """)


## Making upper/lower graphs
st.markdown("#### Visualisation of difference")

st.markdown("The graph also displays the proportional difference in referrals. "
            "An increase in referrals from the comparator group (e.g. Population or baseline), i.e. 'more than expected', appears as blue. "
            "A decrease in referrals, i.e. 'less than expected' appears as red.")

st.markdown("The index of multiple deprivation is presented by the IMD decile of the location of the patient's GP (GP_IMD) "
            "or population-weighted IMD of the patient's GP (Pop_IMD).")

## Baseline v CDC

#set up data for graph
negative_data = merged_referral_file['CDC vs Baseline'].clip(upper=0)
positive_data = merged_referral_file['CDC vs Baseline'].clip(lower=0)

fig, ax = plt.subplots()

# Plot the negative_data and positive_data as bar charts
ax.bar(merged_referral_file.index.values, negative_data, width=1, color='r', label='Less than expected')
ax.bar(merged_referral_file.index.values, positive_data, width=1, color='b', label='More than expected')

# Add a horizontal line at y=0
plt.axhline(y=0.0, color='black', linestyle='-')

# Set labels and title
plt.ylabel('Less than expected          More than expected', fontsize=10)
plt.xlabel(f'{demographic}', fontsize=10)
plt.title(f'CDC vs Baseline: Comparison of patient groups by {demographic}', fontsize=10)

# Add a legend
ax.legend()

# Formatting y-axis tick labels to include %
def format_func(value, tick_number):
    return f'{value}%'

# Apply the custom formatter to the y-axis
ax.yaxis.set_major_formatter(FuncFormatter(format_func))

# Display the Matplotlib figure in Streamlit
st.pyplot(fig)

st.markdown("The CDC vs Baseline comparison describes how the GP referral patterns of the CDC compares to a baseline period at a similar diagnostic service. "
            "This metric accounts for any specifc demographic weighting for particular modalities.")


## Census v CDC

#set up data for graph
negative_data = merged_referral_file['CDC vs Population'].clip(upper=0)
positive_data = merged_referral_file['CDC vs Population'].clip(lower=0)

fig, ax = plt.subplots()

# Plot the negative_data and positive_data as bar charts
ax.bar(merged_referral_file.index.values, negative_data, width=1, color='r', label='Less than expected')
ax.bar(merged_referral_file.index.values, positive_data, width=1, color='b', label='More than expected')

# Add a horizontal line at y=0
plt.axhline(y=0.0, color='black', linestyle='-')

# Set labels and title
plt.ylabel('Less than expected          More than expected', fontsize=10)
plt.xlabel(f'{demographic}', fontsize=10)
plt.title(f'CDC vs Population: Comparison of patient groups by {demographic}', fontsize=10)

# Add a legend
ax.legend()

# Apply the custom formatter to the y-axis
ax.yaxis.set_major_formatter(FuncFormatter(format_func))

# Display the Matplotlib figure in Streamlit
st.pyplot(fig)

st.markdown(f"The CDC vs Population comparison describes how the GP referral patterns of the CDC compares to the population of {local_authority}. "
            "This metric highlights any perpetuating inequalities in access for referrals to the CDC.")


## Data Summary

#Displaying summary of referrals
st.subheader('Summary of referrals', divider='grey')

st.markdown("A summary of referral data is included below for review and quality control. ")



#Set columns
col3, col4 = st.columns(2)

# Display the first 10 rows of the selected columns
col3.subheader('Count of referrals')
col3.dataframe(count_columns.head(10).astype(int), width=300)

# Display the first 10 rows of the selected columns
col4.subheader('Percentage of referrals')
col4.dataframe(ct_formatted_df.head(10), width=300)


