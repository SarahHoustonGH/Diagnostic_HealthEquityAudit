# Code to pull weighted IMD scores for each GP practice across England, 
# rank them nationally, filter the data for a specific local authority and
# calculate percent of total

import fingertips_py as ftp 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

os.chdir("YOUR PATH")

#Read in all weighted IMD scores using Fingertips API
GP_Weighted_IMD_Scores = ftp.retrieve_data.get_data_by_indicator_ids("93553", area_type_id=7, parent_area_type_id=None, profile_id=21, include_sortable_time_periods=None, is_test=False)

#Read in GP practice data to map - This include number of patients registered at each practice
GP_Data = pd.read_csv("GP_Data_Map_summary.csv")

#Rename column in Fingertips data for merging
GP_Weighted_IMD_Scores.rename(columns={'Area Code':'CODE'}, inplace=True)

#Merge data
mergedata = pd.merge(GP_Weighted_IMD_Scores, GP_Data, on='CODE')

# Ranking scores HIGH to low
mergedata['IMD Rank'] = mergedata['Value'].rank(ascending=False)

# Dividing scores into quintiles
mergedata['IMD Weighted GP Decile'] = pd.qcut(mergedata['IMD Rank'], 10, labels=False)

# Adding a 1 as the original cut divides 0-9
mergedata['IMD Weighted GP Decile'] = mergedata['IMD Weighted GP Decile'] + 1

# Assign a local authority
local_authority = "Haringey"

# Apply conditon to filter
condition = (mergedata['LAD21name'] == "Haringey")

# Filter merged dataset for LA
filtered_mergedata_LA = mergedata[condition]

value_counts = filtered_mergedata_LA['IMD Weighted GP Decile'].value_counts()

# Group by IMD decile and aggregate using count and sum
result = filtered_mergedata_LA.groupby('IMD Weighted GP Decile')['NUMBER_OF_PATIENTS'].sum().reset_index()
result.reset_index(drop=True)
result.set_index('IMD Weighted GP Decile', inplace=True)

# Calculate the percentage of total and add it to the result 
result['Percentage'] = (result['NUMBER_OF_PATIENTS'] / (result['NUMBER_OF_PATIENTS'].sum())) * 100

# Create a bar graph to show distrubution of patients
result.plot(kind='bar', y = 'NUMBER_OF_PATIENTS', legend=False)
#plt.show()

result.plot(kind='bar', y = 'Percentage', legend=False)
