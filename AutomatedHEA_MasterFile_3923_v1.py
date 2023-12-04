## 3923 Automated Health Equity Audit v1

# Master file v01

# Combining ReferralSummariser and Census Summarizer modules

# Libraries
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np

# Set wd

#os.chdir('your path')

### Step 1 - Run Referral Summariser

# Import module
import ReferralSummariser_2923_v4 
from ReferralSummariser_2923_v4 import Datasummariser

#List of CSV file paths
csv_files = ["Data/CDCReferralDummy.csv", "Data/ReferralDummy.csv"]  # Replace with actual paths
       
for csv_file_path in csv_files:
    # Extract the filename without extension
    filename = csv_file_path.split(".")[0]
    # Create an instance of the CSVsummariser class for each CSV
    summariser = Datasummariser(csv_file_path)
    # Call the summarise_and_save method to generate and save summaries
    summariser.summarise_and_save(filename,csv_file_path)
    

GPdata_csv_url = 'https://files.digital.nhs.uk/19/AADF93/gp-reg-pat-prac-all.csv'  # Replace with the actual URL of the additional CSV data

# Download the additional CSV data and store it
Datasummariser(csv_file_path).download_GPdata_csv(GPdata_csv_url)

### Step 2 - Run Census Summariser

#Import module
#import CensusSummariser_29823_v2  
from CensusSummariser_29823_v2 import CensusSummariser

## Ask user for local authority input
user_local_authority = str(input("Enter the local authority you'd like to summarize: "))

#Write this local authority for use in Streamlit
with open("Stage1Outputs/user_local_authority.txt", "w") as f:
    f.write(user_local_authority)

# Call the methods
summariser = CensusSummariser()

# Download the Census data
summariser.download_age_sex_csv()
summariser.download_ethnicity_csv()

# Summarize the data
age_data_clean, sex_data_clean, age_sex_data_clean = summariser.summarise_age_sex_csv()

# Provide a local authority for summarization
summariser.summarise_by_la(user_local_authority)

### Step 3 - Referral mapping
from ReferralMapping_211023_v1 import ReferralMapping

referral_mapping = ReferralMapping()
    
mapping_data = referral_mapping.read_mapping_data()
IMD_data = referral_mapping.read_IMD_data()
registration_data = referral_mapping.read_registration_data()
fulldata = referral_mapping.merge_mapping_and_registration(mapping_data, registration_data, IMD_data)
referral_mapping.generate_subset(fulldata)
    
referral_modalities = ["X", "U"]
referral_mapping.process_referral_and_location_data(referral_modalities)
referral_mapping.process_GP_data()


### Step 4 - Run HEA Processor

from HEAProcessor_211023_v1 import HEAProcessor

data_processor = HEAProcessor()
data_processor.merge_process_data(user_local_authority)
data_processor.process_gp_IMD_data(user_local_authority)
data_processor.process_pop_IMD_data(user_local_authority)