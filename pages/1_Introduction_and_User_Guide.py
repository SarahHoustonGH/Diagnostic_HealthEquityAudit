import streamlit as st

st.title(f'Introduction and User Guide')

# Display the description of the project

st.markdown(
    """

    ## Introduction to CDCs

    Community diagnostic centres (CDCs) have been launched across England to tackle the diagnostic backlog and address healthcare inequalities. 
    CDCs and commissioners struggle to identify their baseline of healthcare inequalities and monitor their impact going forwards. 
    This leads to resourcing constraints on teams in the short term and risks minimising the CDC’s impact on healthcare inequalities in the long term. 
    As these are emerging services, the quality of data collected by them to understand their impact is unclear. 
    This product is designed to automate much of this process and support CDCs in understanding their impact on a specific local authority.

    ## Introduction to project

    This Streamlit app allows you to visualize results produced by the HSMA5 Automated Health Equity Audit for CDCs. 
    The product was developed as part of the Health Services Modelling Associates Programme (Cohort 5) by Sarah Houston and Deborah Newton.

    ## User guide
    
    ### Data required

    Dummy data is included in the Github repository for demo purposes. This data has been generated randomly and bears no relation to real referral data.
    To use this code, the following is required:
    -	Referral level data from the CDC
    -	Referral level data from a matched baseline diagnostic service 
    -	Both data must at a minimum contain fields as described below

    The matched baseline service could be a local acute diagnostic service operating in the year before the introduction of the CDC.
    Fields required:
    -	Referral Source: Name of GP practice
    -	Modality: Diagnostic modality. This version of the code supports X (x ray) and U (ultrasound)
    -	Patient GP: GP registration code
    -	Age: Age in years
    -	Patient_Gender: Male, Female or Unknown
    -	Ethnicity_Code: NHS ethnic category (e.g. A)
    -	Ethnicity Description: Full description of code (e.g. White British)
    -	Postcode: GP location postcode

    ### Structure of code

    This analysis is performed in two steps: Processing and Display.
    
"""
)

# Read in process image
image = 'pages\AutoHEA_Process.png'

# Display the image
st.image(image, caption='', use_column_width=True)

st.markdown(
    """
    #### Step 1: Processing

    - Download the Github folder
    - Replace the dummy data files with
    - Run the AutomatedHEA_MasterFile: This will run all the modules required to generate outputs for the Streamlit application.
    
    At this stage, the user also inputs the local authority of interest. This will be used as the base population which referral rates will be compared to. The CDC of interest should be within this local authority.

    #### Step 2: Display

    - Run the HEA_Streamlit2 file through Anaconda
    - The summary outputs from Step 1 will be used to build content for display in Streamlit

    Due to the unique nature of CDCs which would be expected to host multiple diagnostic modalities, 
    provisional modalities of X ray and ultrasound have been included for disaggregation of results, however these could be adapted for future versions.

    ### Limitations of analysis

    1.	Gender is equated with sex in the analysis due to disparities in definition between NHS and Census data, potentially overlooking nuanced gender-related disparities.
    2.	Index of Multiple Deprivation data based on GP location (GP_IMD) assumes patients are exclusively from that Lower Super Output Area (LSOA). Population weighted IMD (Pop_IMD) has been extracted from Fingertips (ONS).
    3.	GP location data has been extracted from a publication by NHS Digital from 
    4.	GP location was based on registered practice location, which does not reflect branch practices.
    5.	Data from other diagnostic services in the region is not included in the analysis. This means we are unable to determine if the CDC is effectively addressing health inequalities or merely shifting care between services in the region.
    6.	This analysis does not attempt to quantify "unmet need", patients who should access diagnostics but do not. 
    7.	This analysis assumes that the CDC should be a general service equally accessed by all demographic groups due to the diverse modalities and conditions it serves, however some services may be weighted towards specific groups, e.g. older patients.
    8.	Potential barriers to access, such as language and disability, are not explored due to lack of data availability, limiting the understanding of disparities related to these factors.
    9.	Intersectional analysis is not included in this analysis but may be beneficial due to the nuanced interactions between multiple factors that contribute to healthcare inequalities.
    10.	Equity audits should also consider not just quantitative analysis such as presented here but also include qualitative engagement with local communities to understand potential barriers in referral and access.
    11.	Broad ethnic categories are used to describe populations in this project, however ethnic and cultural diversity cannot be described by broad ethnic categories alone. Broad ethnic categories were chosen for accurate mapping between the NHS Ethnic Category to Ethnic Group as recorded by the ONS in the Census.
    12.	This project focusses on equity of referrals, however increasing referrals to diagnostics is only the first step to improving health outcomes in the region. Similar analysis should be performed to explore access (i.e. attendances), experience and outcomes across different demographic cohorts.

    ### Next steps

    This project is still under development as of December 2023. Potential next steps are described below.

    -	Flexible modality selection
    -	Combine Step 1 (Processing, Python) with Step 2 (Display, Streamlit) to one user interface
    -	Expand “base population” to include more than one local authority
    -	Include data to highlight rural/urban disparities of referral
    -	Expand analysis to more ethnic categories
    -	Include more intersectional analysis (e.g. age vs gender, ethnicity vs deprivation)

    ### Contact us
    
    If you would like to learn more about the project or contact the team for further details, please email sarah.houston.16@ucl.ac.uk

    
"""
)