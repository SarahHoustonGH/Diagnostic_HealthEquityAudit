#Code to convert postcode to lat/long for UK postcodes

import pgeocode
import os
import pandas as pd

nomi = pgeocode.Nominatim('gb')

os.chdir("...")

Ref_Data = pd.read_csv("GPSummaryReferralData_U_Map.csv")

# List of postcodes
postcodes = Ref_Data["Postcode"]

# Create empty columns for latitude and longitude
Ref_Data["Latitude"] = None
Ref_Data["Longitude"] = None

# Loop through the list of postcodes and query the latitude and longitude
for i, postcode in enumerate(postcodes):
    location_info = nomi.query_postal_code(postcode)
    
    if not location_info.empty:
        Ref_Data.at[i, "Latitude"] = location_info.latitude
        Ref_Data.at[i, "Longitude"] = location_info.longitude

