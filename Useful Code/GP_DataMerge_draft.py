## Combining GP datasets


import os
import pandas as pd

# Read the CSV file
Mapping_data = pd.read_csv("Data/x-boundary-mapping-2023-24-v1.csv")
Registration_data = pd.read_csv("Stage1Outputs/GPdata.csv")


# View the first 5 rows
Mapping_data.head()
Registration_data.head()

#rename practice to code
Mapping_data = Mapping_data.rename(columns={'Practice': 'CODE'}) 

fulldata = pd.merge(Mapping_data, Registration_data, on='CODE')

fulldata.head()

#Generate a subset of required columns

fulldata_subset = fulldata[['CODE', 'GP practice name', 'Postcode','ICB23ons',
                            'LAD21','LAD21name',
                            'ICB23','ICB23name','LSOA11','MSOA11','POSTCODE',
                            'NUMBER_OF_PATIENTS']]

fulldata_subset.to_csv('Stage1Outputs/GP_Data_Map_summary.csv')

referral_modality = ["X", "U"]

#Read in GP referrals for CDC and baseline
for modality in referral_modality:
    Ref_Data = pd.read_csv(f"Stage1Outputs/ReferralDummy_{modality}_GPCode_summary.csv")
    CDC_Data = pd.read_csv(f"Stage1Outputs/CDCReferralDummy_{modality}_GPCode_summary.csv")

    #change column headers for full data
    fulldata_subset = fulldata_subset.rename(columns={'CODE': 'Patient GP'}) 

    #
    GPSummaryReferralData = pd.merge(fulldata_subset, Ref_Data, on='Patient GP')
    GPSummaryReferralData = pd.merge(GPSummaryReferralData, CDC_Data, on='Patient GP')

    GPSummaryReferralData.to_csv(f'Stage1Outputs/GPSummaryReferralData_{modality}_Map.csv')