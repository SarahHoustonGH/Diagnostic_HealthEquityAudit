import pandas as pd
import os

#set wd

# Define a list of modalitys for the referral files
referral_modality = ["X", "U"]
demographics = ["age", "gender", "ethnicity"]

# Loop through the modalitys
for modality in referral_modality:
    for demographic in demographics:
        # Define the file names for the CSVs
        cdc_referral_file = f"Stage1Outputs/CDCReferralDummy_{modality}_{demographic}_summary.csv"
        referral_file = f"Stage1Outputs/ReferralDummy_{modality}_{demographic}_summary.csv"
        census_file = f"Stage1Outputs/Census_{demographic}_summary_Haringey.csv"

        # Read CSV files into Pandas DataFrames
        df_cdc_referral = pd.read_csv(cdc_referral_file)
        df_referral = pd.read_csv(referral_file)
        df_census = pd.read_csv(census_file)

        # Rename the first column to the demographic name
        df_cdc_referral.columns.values[0] = demographic
        df_cdc_referral.columns.values[1] = "CDC_Count"
        df_referral.columns.values[0] = demographic
        df_census.columns.values[0] = demographic
       
        # Merge the data into a single table
        merged_df = pd.merge(df_census, df_referral, on=demographic, how='outer')
        merged_df = pd.merge(merged_df, df_cdc_referral, on=demographic, how='outer')

        # Calculate percentages of column totals
        for column in merged_df.columns[1:]:
            merged_df[column + '_percentage'] = (merged_df[column] / merged_df[column].sum()) * 100

        # Write merged and percentage tables to CSV
        merged_df.to_csv(f"Stage1Outputs/Merged_{modality}_{demographic}.csv", index=False)

# End of loop
