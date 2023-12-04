import os
import pandas as pd
import pgeocode
import logging 
from geopy.geocoders import Nominatim
import requests
import time

class ReferralMapping:
    def __init__(self):
        self.data_folder = "Stage1Outputs/"  # Hardcoded data folder
        self.nomi = pgeocode.Nominatim('gb')
        self.fulldata_subset = None
        self.geolocator = Nominatim(user_agent="myGeocoder")
        self.api_key = 'YOUR API KEY'

    def read_mapping_data(self):
        mapping_data = pd.read_csv("Data/x-boundary-mapping-2023-24-v1.csv")
        return mapping_data
    
    def read_IMD_data(self):
        IMD_data = pd.read_csv("Data/IMD_LSOA_Lookup.csv")
        return IMD_data

    def read_registration_data(self):
        registration_data = pd.read_csv(os.path.join(self.data_folder, "GPdata.csv"))
        return registration_data

    def merge_mapping_and_registration(self, mapping_data, registration_data, IMD_data):
        mapping_data = mapping_data.rename(columns={'Practice': 'CODE'})
        fulldata = pd.merge(mapping_data, registration_data, on='CODE')
        fulldata = pd.merge(fulldata, IMD_data, on='LSOA11')
        return fulldata

    def generate_subset(self, fulldata):
        self.fulldata_subset = fulldata[['CODE', 'GP practice name', 'Postcode', 'ICB23ons', 'LAD21', 'LAD21name',
                                    'ICB23', 'ICB23name', 'LSOA11', 'MSOA11', 'POSTCODE', 'NUMBER_OF_PATIENTS', 'IMD2019 Decile']]
        self.fulldata_subset.to_csv('Stage2Outputs/GP_Data_Map_summary.csv')
        return self.fulldata_subset


    # def process_referral_and_location_data(self, referral_modalities):
    #     for modality in referral_modalities:
    #         ref_data = pd.read_csv(os.path.join(self.data_folder, f"ReferralDummy_{modality}_GPCode_summary.csv"))
    #         cdc_data = pd.read_csv(os.path.join(self.data_folder, f"CDCReferralDummy_{modality}_GPCode_summary.csv"))
                
    #         self.fulldata_subset = self.fulldata_subset.rename(columns={'CODE': 'Patient GP'})
          
    #         gpsummary_referral_data = pd.merge(self.fulldata_subset, ref_data, on='Patient GP')
    #         gpsummary_referral_data = pd.merge(gpsummary_referral_data, cdc_data, on='Patient GP', suffixes=('_Referrals_Baseline','_Referrals_CDC'))
       
    #         # Add location info to the merged data
    #         gpsummary_referral_data["Latitude"] = None
    #         gpsummary_referral_data["Longitude"] = None
            
    #         for index, row in gpsummary_referral_data.iterrows():
    #             postcode = row["Postcode"]
    #             location_info = self.get_lat_long(postcode)  # Assume get_lat_long makes the API call
    #             if location_info is not None:
    #                 gpsummary_referral_data.at[index, "Latitude"] = location_info['latitude']
    #                 gpsummary_referral_data.at[index, "Longitude"] = location_info['longitude']
    #             else:
    #                 print(f"No location info for postcode: {postcode}")
    #                 # Handle empty location_info if needed

    #         # Write the final CSV
    #         output_file = f'Stage2Outputs/GPSummaryReferralData_{modality}_Map.csv'
    #         gpsummary_referral_data.to_csv(output_file, index=False)

    # def get_lat_long(self, postcode):
    #     # Implement your API call here to fetch latitude and longitude based on the postcode
    #     # Use requests library or any suitable method to fetch the data
    #     # Example:
    #     response = requests.post("https://api.postcodes.io/postcodes", json={"postcodes": [postcode]})
    #     if response.status_code == 200:
    #         # Extract latitude and longitude from the API response
    #         location_data = response.json()
    #         latitude = location_data['result'][0]['result_latitude']
    #         longitude = location_data['result'][0]['result_longitude']
    #         return {"latitude": latitude, "longitude": longitude}
    #     else:
    #         print(f"Failed to fetch location info for postcode: {postcode}")
    #         return None
    
    def get_lat_long(self, postcodes, max_retries=3):
        batched_location_info = {"latitude": [], "longitude": []}
        for i in range(0, len(postcodes), 100):
            batch_postcodes = postcodes[i:i + 100]   # Get a batch of 100 postcodes
            attempt = 0
            while attempt < max_retries:
                response = requests.post("https://api.postcodes.io/postcodes", json={"postcodes": batch_postcodes})
                if response.status_code == 200:
                    location_data = response.json()
                    for result in location_data['result']:
                        if 'result' in result and 'latitude' in result['result'] and 'longitude' in result['result']:
                            batched_location_info['latitude'].append(result['result']['latitude'])
                            batched_location_info['longitude'].append(result['result']['longitude'])
                        else:
                            print("Skipping incomplete data for some postcodes in this batch")
                    break  # Exit the loop if successful
                else:
                    print(f"Failed to fetch location info for some postcodes in this batch. Retrying ({attempt + 1}/{max_retries})...")
                    attempt += 1
                    time.sleep(1)  # Wait for some time before retrying
      
        if batched_location_info is None:
            print("No location information retrieved.")
            return {"latitude": [], "longitude": []}  # Return empty lists as a default
       
        return batched_location_info

        
    def process_referral_and_location_data(self, referral_modalities):
        for modality in referral_modalities:
            ref_data = pd.read_csv(os.path.join(self.data_folder, f"ReferralDummy_{modality}_GPCode_summary.csv"))
            cdc_data = pd.read_csv(os.path.join(self.data_folder, f"CDCReferralDummy_{modality}_GPCode_summary.csv"))

            self.fulldata_subset = self.fulldata_subset.rename(columns={'CODE': 'Patient GP'})

            gpsummary_referral_data = pd.merge(self.fulldata_subset, ref_data, on='Patient GP')
            gpsummary_referral_data = pd.merge(gpsummary_referral_data, cdc_data, on='Patient GP', suffixes=('_Referrals_Baseline', '_Referrals_CDC'))

            postcodes = gpsummary_referral_data['Postcode'].tolist()  # Get list of postcodes
            batch_size = 100
            for i in range(0, len(postcodes), batch_size):
                batch_postcodes = postcodes[i:i + batch_size]  # Get a batch of 100 postcodes
                location_info = self.get_lat_long(batch_postcodes)  # Get location info for this batch of postcodes
                
                # Add location info to the merged data for this batch
                start_idx = i
                end_idx = min(i + batch_size, len(postcodes))
                gpsummary_referral_data.loc[start_idx:end_idx - 1, 'Latitude'] = location_info['latitude']
                gpsummary_referral_data.loc[start_idx:end_idx - 1, 'Longitude'] = location_info['longitude']

            # Write the final CSV
            output_file = f'Stage2Outputs/GPSummaryReferralData_{modality}_Map.csv'
            gpsummary_referral_data.to_csv(output_file, index=False)

    def process_GP_data(self):
        gp_location_data = pd.read_csv("Stage1Outputs/GPdata.csv")

        # Filter out specific postcodes with known error
        postcodes_to_filter = ['WA8 4NJ', 'L28 1ST']  # Replace these with the postcodes to filter out
        gp_location_data = gp_location_data[~gp_location_data['POSTCODE'].isin(postcodes_to_filter)]

        # Add location info to the merged data
        postcodes_gp = gp_location_data['POSTCODE'].tolist()
        
        # Accumulate latitude and longitude values
        batch_size_2 = 50
        latitudes = []
        longitudes = []

        for i in range(0, len(postcodes_gp), batch_size_2):
            if i + batch_size_2 < len(postcodes_gp):
                batch_postcodes_gp = postcodes_gp[i:i + batch_size_2]
            else:
                batch_postcodes_gp = postcodes_gp[i:]

            location_info_gp = self.get_lat_long(batch_postcodes_gp)

            latitudes.extend(location_info_gp['latitude'])
            longitudes.extend(location_info_gp['longitude'])

        # Assign accumulated lists to DataFrame columns
        gp_location_data['Latitude'] = latitudes
        gp_location_data['Longitude'] = longitudes

        # Write to CSV after processing
        output_file = "Stage2Outputs/GP_location_data.csv"
        gp_location_data.to_csv(output_file, index=False)

        print('Referral mapping complete. Please hold.')



if __name__ == "__main__":
    referral_mapping = ReferralMapping()
    
    mapping_data = referral_mapping.read_mapping_data()
    IMD_data = referral_mapping.read_IMD_data()
    registration_data = referral_mapping.read_registration_data()
    fulldata = referral_mapping.merge_mapping_and_registration(mapping_data, registration_data, IMD_data)
    referral_mapping.generate_subset(fulldata)
    
    referral_modalities = ["X", "U"]
    referral_mapping.process_referral_and_location_data(referral_modalities)
    #referral_mapping.process_GP_data()

