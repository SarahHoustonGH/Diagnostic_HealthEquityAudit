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

    def merge_process_data(self, user_local_authority):
        for modality in self.referral_modalities:
            for demographic in self.demographics:
                cdc_referral_file = f"Stage1Outputs/CDCReferralDummy_{modality}_{demographic}_summary.csv"
                referral_file = f"Stage1Outputs/ReferralDummy_{modality}_{demographic}_summary.csv"
                census_file = f"Stage1Outputs/Census_{demographic}_summary_{user_local_authority}.csv"

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

                merged_df.to_csv(f"Stage2Outputs/Merged_{modality}_{demographic}.csv", index=False)
            print('Referral data for HEA combined')

    # Function to create IMD table for local authority
    def process_gp_IMD_data(self, user_local_authority):
        
        #Read and filter data
        gp_data_file = pd.read_csv("Stage2Outputs\GP_Data_Map_summary.csv")
        filtered_GP_data = gp_data_file[gp_data_file['LAD21name'] == user_local_authority]

        #Summarise based on IMD
        IMD_summary_table = pd.pivot_table(filtered_GP_data, values='NUMBER_OF_PATIENTS', index=['IMD2019 Decile'],
                     aggfunc="sum")
        IMD_summary_table.index.names = ['GP_IMD']
        #IMD_summary_table['Patient_percentage'] = (IMD_summary_table['NUMBER_OF_PATIENTS'] / IMD_summary_table['NUMBER_OF_PATIENTS'] .sum()) * 100
        
        IMD_summary_table.to_csv("Stage2Outputs/IMD_summary_table.csv")

        for modality in self.referral_modalities:    
            df_cdc_referral = pd.read_csv(f"Stage1Outputs/CDCReferralDummy_{modality}_IMD_summary.csv")
            df_referral = pd.read_csv(f"Stage1Outputs/ReferralDummy_{modality}_IMD_summary.csv")

            df_cdc_referral.columns.values[0] = "GP_IMD"
            df_cdc_referral.columns.values[1] = "CDC_Count"
            df_referral.columns.values[0] = "GP_IMD"
            df_referral.columns.values[1] = "Baseline_Count"
            
            merged_df = pd.merge(IMD_summary_table, df_referral, on='GP_IMD', how='outer')
            merged_df = pd.merge(merged_df, df_cdc_referral, on='GP_IMD', how='outer')
            
            for column in merged_df.columns[1:]:
                    merged_df[column + '_percentage'] = (merged_df[column] / merged_df[column].sum()) * 100

            merged_df.to_csv(f"Stage2Outputs/Merged_{modality}_GP_IMD.csv", index=False)
        print('Referral data per GP for HEA combined')

    # Function to create IMD table for local authority
    def process_pop_IMD_data(self, user_local_authority):
        
        #Read and filter data
        pop_data_file = pd.read_csv("Data\IMD_Population_2021.csv")
        filtered_pop_data = pop_data_file[pop_data_file['Local Authority'] == user_local_authority]

        #Summarise based on IMD
        IMD_summary_table_pop = pd.pivot_table(filtered_pop_data, values='Total', index=['IMD'],
                     aggfunc="sum")
        IMD_summary_table_pop.index.names = ['Pop_IMD']

        #IMD_summary_table['Patient_percentage'] = (IMD_summary_table['NUMBER_OF_PATIENTS'] / IMD_summary_table['NUMBER_OF_PATIENTS'] .sum()) * 100
        #IMD_summary_table = IMD_summary_table.rename(columns={'IMD2019 Decile':'IMD Decile'})
        IMD_summary_table_pop.to_csv("Stage2Outputs/IMD_summary_table_pop.csv")

        for modality in self.referral_modalities:    
            df_cdc_referral = pd.read_csv(f"Stage1Outputs/CDCReferralDummy_{modality}_IMD_summary.csv")
            df_referral = pd.read_csv(f"Stage1Outputs/ReferralDummy_{modality}_IMD_summary.csv")

            df_cdc_referral.columns.values[0] = "Pop_IMD"
            df_cdc_referral.columns.values[1] = "CDC_Count"
            df_referral.columns.values[0] = "Pop_IMD"
            df_referral.columns.values[1] = "Baseline_Count"

            
            merged_df = pd.merge(IMD_summary_table_pop, df_referral, on='Pop_IMD', how='outer')
            merged_df = pd.merge(merged_df, df_cdc_referral, on='Pop_IMD', how='outer')
            
            for column in merged_df.columns[1:]:
                    merged_df[column + '_percentage'] = (merged_df[column] / merged_df[column].sum()) * 100

            merged_df.to_csv(f"Stage2Outputs/Merged_{modality}_Pop_IMD.csv", index=False)
        print('HEA Processor complete. End of Step 1. Please use the Streamlit app to visualise results.')


if __name__ == "__main__":
    data_processor = HEAProcessor()
    data_processor.merge_process_data()

    #adding example LA for testing
    user_local_authority = "Haringey"

    data_processor.process_gp_IMD_data(user_local_authority)

    data_processor.process_pop_IMD_data(user_local_authority)