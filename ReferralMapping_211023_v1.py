import os
import pandas as pd
import pgeocode
import logging 
from geopy.geocoders import Nominatim

class ReferralMapping:
    def __init__(self):
        self.data_folder = "Stage1Outputs/"  # Hardcoded data folder
        self.nomi = pgeocode.Nominatim('gb')
        self.fulldata_subset = None
        self.geolocator = Nominatim(user_agent="myGeocoder")

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
        #             location_info = self.nomi.query_postal_code(postcode)
        #             if not location_info.empty:
        #                 gpsummary_referral_data.at[index, "Latitude"] = location_info.latitude
        #                 gpsummary_referral_data.at[index, "Longitude"] = location_info.longitude
        #             else:
        #                 # Handle empty location_info - log, skip, or set default values
        #                 logging.warning(f"No location info for postcode: {postcode}")
        #                 # For example:
        #                 # gpsummary_referral_data.at[index, "Latitude"] = 0.0
        #                 # gpsummary_referral_data.at[index, "Longitude"] = 0.0
                
        #         # Write the final CSV
        #         output_file = f'Stage2Outputs/GPSummaryReferralData_{modality}_Map.csv'
        #         gpsummary_referral_data.to_csv(output_file, index=False)

    def process_referral_and_location_data(self, referral_modalities):
        for modality in referral_modalities:
            ref_data = pd.read_csv(os.path.join(self.data_folder, f"ReferralDummy_{modality}_GPCode_summary.csv"))
            cdc_data = pd.read_csv(os.path.join(self.data_folder, f"CDCReferralDummy_{modality}_GPCode_summary.csv"))
            
            self.fulldata_subset = self.fulldata_subset.rename(columns={'CODE': 'Patient GP'})
            
            gpsummary_referral_data = pd.merge(self.fulldata_subset, ref_data, on='Patient GP')
            gpsummary_referral_data = pd.merge(gpsummary_referral_data, cdc_data, on='Patient GP', suffixes=('_Referrals_Baseline','_Referrals_CDC'))
            
            # Add location info to the merged data
            gpsummary_referral_data["Latitude"] = None
            gpsummary_referral_data["Longitude"] = None
            
            for index, row in gpsummary_referral_data.iterrows():
                postcode = row["Postcode"]
                location_info = self.get_lat_long(postcode)
                if location_info is not None:
                    gpsummary_referral_data.at[index, "Latitude"] = location_info.latitude
                    gpsummary_referral_data.at[index, "Longitude"] = location_info.longitude
                else:
                    # Handle empty location_info - log, skip, or set default values
                    print(f"No location info for postcode: {postcode}")
                    # For example:
                    # gpsummary_referral_data.at[index, "Latitude"] = 0.0
                    # gpsummary_referral_data.at[index, "Longitude"] = 0.0
            
            # Write the final CSV
            output_file = f'Stage2Outputs/GPSummaryReferralData_{modality}_Map.csv'
            gpsummary_referral_data.to_csv(output_file, index=False)

    def get_lat_long(self, postcode):
        try:
            location = self.geolocator.geocode({"postalcode": postcode, "country": "United Kingdom"})
            return location
        except Exception as e:
            print(f"Error fetching location for {postcode}: {e}")
            return None
        
    def process_GP_data(self):
        
            gp_location_data = pd.read_csv("Stage1Outputs/GPdata.csv")

            # Add location info to the merged data
            postcodes = gp_location_data["POSTCODE"]
            gp_location_data["Latitude"] = None
            gp_location_data["Longitude"] = None
            
            for i, postcode in enumerate(postcodes):
                location_info = self.nomi.query_postal_code(postcode)
                if not location_info.empty:
                    gp_location_data.at[i, "Latitude"] = location_info.latitude
                    gp_location_data.at[i, "Longitude"] = location_info.longitude
            
            # Write the final CSV
            output_file = (f'Stage2Outputs/GP_location_data.csv')
            gp_location_data.to_csv(output_file, index=False)


if __name__ == "__main__":
    referral_mapping = ReferralMapping()
    
    mapping_data = referral_mapping.read_mapping_data()
    IMD_data = referral_mapping.read_IMD_data()
    registration_data = referral_mapping.read_registration_data()
    fulldata = referral_mapping.merge_mapping_and_registration(mapping_data, registration_data, IMD_data)
    referral_mapping.generate_subset(fulldata)
    
    referral_modalities = ["X", "U"]
    referral_mapping.process_referral_and_location_data(referral_modalities)
    referral_mapping.process_GP_data()

