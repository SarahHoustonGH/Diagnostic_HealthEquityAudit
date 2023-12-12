
# Data extracted from 
# https://opendatacommunities.org/slice/observations.csv?&dataset=http%3A%2F%2Fopendatacommunities.org%2Fdata%2Fsocietal-wellbeing%2Fimd2019%2Findices&http%3A%2F%2Fopendatacommunities.org%2Fdef%2Fontology%2Ftime%2FrefPeriod=http%3A%2F%2Freference.data.gov.uk%2Fid%2Fyear%2F2019&http%3A%2F%2Fpurl.org%2Flinked-data%2Fcube%23measureType=http%3A%2F%2Fopendatacommunities.org%2Fdef%2Fontology%2Fcommunities%2Fsocietal_wellbeing%2Fimd%2FdecObs
#and combined with

# Read in IMD pop data

# Read in Excel data - Matching GP practice to LA
# From https://www.england.nhs.uk/wp-content/uploads/2023/01/x-boundary-mapping-2023-24-v1.xlsx

# Creat new file - GP code, GP name, IMD, LSOA, Practice reg, LA
# Another file - LSOA, IMD, population size, LA

# import packages
import os
import pandas as pd
import requests
#import rpy2
import numpy as np

# set wd
#os.chdir("YOUR PATH")

# pull in the datasets

NHSDMapping = pd.read_csv("x-boundary-mapping-2023-24-v1.csv")
IMDCensusData = pd.read_csv("IMD_Population_2021.csv")
GPTotals = pd.read_csv("Stage1Outputs\GPdata.csv")


#rename columns for merging
IMDCensusData.rename(columns={"mnemonic": "LSOA11","Total":"TotalCensusPop2021","IMD":"LSOA_IMD"}, inplace=True)       

#merge mapping data and IMD data
GPLevelData = pd.merge(NHSDMapping, IMDCensusData, on='LSOA11')

#rename columns for merging
GPLevelData.rename(columns={"Practice": "CODE"}, inplace=True) 

#merge GP data on ICB and total patient population
GPLevelDataPop = pd.merge(GPLevelData, GPTotals, on='CODE')

