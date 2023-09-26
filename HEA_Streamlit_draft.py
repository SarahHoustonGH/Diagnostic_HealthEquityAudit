import streamlit as st
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt

st.title('Health Equity Audit of CDC in LA')

#Write some introductory text

#Connect this to main code later
local_authority = "Haringey"

# Define the header and main text
header_text = "Welcome to the CDC Health Equity Audit"
main_text = (
    "This Streamlit app allows you to visualize results produced by the HSMA5 Health Equity Audit for CDCs."
    " Please select your modality and demographic of interest below."
)

# Display the header and main text using markdown
st.markdown(f"# {header_text}")
st.markdown(main_text)

#Create buttons
modality = st.radio(
    "What modality would you like to view?",
    ["X", "U"])

demographic = st.radio(
    "What demographic would you like to disaggregate by?",
    ["age", "gender", "ethnicity"])


#Read in data
merged_referral_file_name = f"Stage1Outputs/Merged_{modality}_{demographic}.csv"        
merged_referral_file = pd.read_csv(merged_referral_file_name)

st.dataframe(merged_referral_file.head())





#streamlit run HEA_Streamlit_draft.py


