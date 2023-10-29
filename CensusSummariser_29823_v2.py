import os
import pandas as pd
import numpy as np
import requests

class CensusSummariser:
    def __init__(self):
        self.age_sex_csv_filename = "Stage1Outputs/age_sex_data_census.csv"
        self.ethnicity_csv_filename = "Stage1Outputs/ethnicity_data_census.csv"
        self.age_clean_csv_filename = "Stage1Outputs/age_data_clean_census.csv"
        self.sex_clean_csv_filename = "Stage1Outputs/sex_data_clean_census.csv"
        self.age_sex_data = None
        self.age_data_clean = None
        self.sex_data_clean = None

    # Downloads the age/sex Census 2021 data by local authority
    def download_age_sex_csv(self):
        # Fetch the CSV data from the URL
        age_sex_response = requests.get(
            'https://www.nomisweb.co.uk/api/v01/dataset/NM_2300_1.data.csv?date=latest&geography=650117121...650117294&c2021_age_92=0...91&c_sex=0...2&measures=20100')
        
        # Check if the request was successful
        if age_sex_response.status_code == 200:
            # Save the downloaded data to the CSV file
            with open(self.age_sex_csv_filename, 'wb') as f:
                f.write(age_sex_response.content)
        else:
            print(f"Failed to download age-sex CSV data. Status code: {age_sex_response.status_code}")
    print("Age/sex saving complete")

    # Downloads the ethnicity Census 2021 data by local authority
    def download_ethnicity_csv(self):
        # Fetch the CSV data from the URL
        response = requests.get('https://www.nomisweb.co.uk/api/v01/dataset/NM_2132_1.data.csv?date=latest&geography=1774190593...1774190597,1774190637,1774190646,1774190675...1774190678,1774190691,1774190598...1774190601,1774190638,1774190639,1774190652,1774190653,1774190656...1774190670,1774190734,1774190602...1774190606,1774190654,1774190671...1774190674,1774190686...1774190690,1774190607...1774190610,1774190650,1774190651,1774190726,1774190735,1774190736,1774190738,1774190611...1774190613,1774190640,1774190679...1774190685,1774190740,1774190743,1774190745,1774190621...1774190624,1774190644,1774190645,1774190725,1774190729,1774190732,1774190737,1774190741,1774190692...1774190724,1774190625...1774190636,1774190649,1774190728,1774190731,1774190733,1774190739,1774190742,1774190744,1774190614...1774190620,1774190641...1774190643,1774190647,1774190648,1774190655,1774190727,1774190730,1774190746...1774190767&c2021_eth_20=0,1001,1...5,1002,6...8,1003,9...12,1004,13...17,1005,18,19&c2021_age_6=0&c_sex=0&measures=20100')
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the downloaded data to the CSV file
            with open(self.ethnicity_csv_filename, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Failed to download ethnicity CSV data. Status code: {response.status_code}")
    print("Ethnicity saving complete")


    def summarise_age_sex_csv(self):
        # Read the CSV data into a pandas DataFrame
        self.age_sex_data = pd.read_csv(self.age_sex_csv_filename, index_col=None)

        # Create a new column called age range 
        self.age_sex_data['Age_range'] = pd.cut(self.age_sex_data['C2021_AGE_92'], 
                                   bins=[-1, 0, 19, 30, 40, 50, 60, 70, 80, 90, 91], 
                                   labels=['Total', '0-17', '18-29', '30-39',
                                            '40-49', '50-59', '60-69', '70-79', 
                                            '80-89', '90+'])
        
        # choose only the relevant rows
        self.age_data_clean = self.age_sex_data[self.age_sex_data['C_SEX_NAME'].
                                                apply(lambda x: 'All persons' in x)]
        self.sex_data_clean = self.age_sex_data[self.age_sex_data['C2021_AGE_92_NAME'].
                                                apply(lambda x: 'Total' in x)]

        # pivot for age x sex
        pivot_table = pd.pivot_table(self.age_sex_data, values='OBS_VALUE',
         index=['Age_range'], columns=['C_SEX_NAME'], aggfunc='sum')

        # write to csv
        self.age_data_clean.to_csv(self.age_clean_csv_filename)  
        self.sex_data_clean.to_csv(self.sex_clean_csv_filename)
        pivot_table.to_csv('Stage1Outputs/age_sex_pivot.csv') 

        return self.age_data_clean, self.sex_data_clean, self.age_sex_data
    print("data check")

    #Summarise based on LA
    def summarise_by_la(self, local_authority):
        ethnicity_data = pd.read_csv(self.ethnicity_csv_filename, index_col=None)

        # Create a new column to distingush ethnic group to ethnic category
        ethnicity_data["ethnic_group"] = np.where(ethnicity_data['C2021_ETH_20'] > 1000, 
                                                  "Ethnic Group", "Ethnic Category")


        # summarise age data
        age_filtered_data = self.age_data_clean[self.age_data_clean['GEOGRAPHY_NAME'].
                                                apply(lambda x: local_authority in x)]
        age_summary = age_filtered_data.groupby("Age_range")["OBS_VALUE"].sum()

        # summarise sex data
        sex_filtered_data = self.sex_data_clean[self.sex_data_clean['GEOGRAPHY_NAME'].
                                                apply(lambda x: local_authority in x)]
        sex_summary = sex_filtered_data.groupby("C_SEX_NAME")["OBS_VALUE"].sum()

        # summarise ethnicity data
        ethnicity_filtered_data = ethnicity_data[ethnicity_data['GEOGRAPHY_NAME'].
                                                 apply(lambda x: local_authority in x)]
        ethnicity_filtered_data = ethnicity_filtered_data.loc[ethnicity_filtered_data['ethnic_group'] == "Ethnic Group"]
        eth_summary = ethnicity_filtered_data.groupby("C2021_ETH_20_NAME")["OBS_VALUE"].sum()
        

        # summarise age x sex
        age_sex_pivot_table = pd.pivot_table(self.age_sex_data, values='OBS_VALUE', index='Age_range',
                            columns = "C_SEX_NAME", aggfunc='sum')

        # save summaries
        sex_summary.to_csv('Stage1Outputs/Census_gender_summary_'+ local_authority +'.csv')  
        age_summary.to_csv('Stage1Outputs/Census_age_summary_'+ local_authority +'.csv') 
        eth_summary.to_csv('Stage1Outputs/Census_ethnicity_summary_'+ local_authority +'.csv')  
        age_sex_pivot_table.to_csv('Stage1Outputs/Census_pivot_summary_'+ local_authority +'.csv')
        
        return age_summary, sex_summary, eth_summary, age_sex_pivot_table
    print('Census data filtered')
