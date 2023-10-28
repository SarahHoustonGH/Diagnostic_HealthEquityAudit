import pandas as pd
import os

#os.chdir('yourpath')

class HEAProcessor:
    def __init__(self):
        self.referral_modalities = ["X", "U"]
        self.demographics = ["age", "gender", "ethnicity"]
        self.name_mapping = {
            'Asian, Asian British or Asian Welsh': 'Asian',
            'Black, Black British, Black Welsh, Caribbean or African': 'Black',
            'Mixed or Multiple ethnic groups': 'Mixed',
            'Other ethnic group': 'Other'
        }

    def merge_process_data(self):
        for modality in self.referral_modalities:
            for demographic in self.demographics:
                cdc_referral_file = f"Stage1Outputs/CDCReferralDummy_{modality}_{demographic}_summary.csv"
                referral_file = f"Stage1Outputs/ReferralDummy_{modality}_{demographic}_summary.csv"
                census_file = f"Stage1Outputs/Census_{demographic}_summary_Haringey.csv"

                df_cdc_referral = pd.read_csv(cdc_referral_file)
                df_referral = pd.read_csv(referral_file)
                df_census = pd.read_csv(census_file)

                df_cdc_referral.columns.values[0] = demographic
                df_cdc_referral.columns.values[1] = "CDC_Count"
                df_referral.columns.values[0] = demographic
                df_referral.columns.values[1] = "Baseline_Count"
                df_census.columns.values[0] = demographic
                df_census.columns.values[1] = "Census_Count"

                df_census[demographic] = df_census[demographic].replace(self.name_mapping)

                merged_df = pd.merge(df_census, df_referral, on=demographic, how='outer')
                merged_df = pd.merge(merged_df, df_cdc_referral, on=demographic, how='outer')

                merged_df = merged_df[~merged_df[demographic].str.contains('Total|All persons')]

                for column in merged_df.columns[1:]:
                    merged_df[column + '_percentage'] = (merged_df[column] / merged_df[column].sum()) * 100

                merged_df.to_csv(f"Stage1Outputs/Merged_{modality}_{demographic}.csv", index=False)

if __name__ == "__main__":
    data_processor = HEAProcessor()
    data_processor.merge_process_data()