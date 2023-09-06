import os
import pandas as pd
import requests
#import rpy2
import pandas as pd
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#pip install rpy2

# set wd
#os.chdir('your wd')

class Datasummariser:
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)
        self.additional_csv_filename = "Stage1Outputs/GPdata.csv"
        self.Ethnicity_LUT = pd.read_csv("LUT\Ethnicity_LUT.csv")
        self.PostcodeIMD = None
        self.mergedata = None
        self.fulldata = None


    def download_GPdata_csv(self, GPdata_csv_url):
        # Fetch the additional CSV data from the provided URL
        response = requests.get(GPdata_csv_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the downloaded data to the additional CSV file
            with open(self.additional_csv_filename, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Failed to download additional CSV data. Status code: {response.status_code}")

    def ConvertPostcodeIMD(self):
        
        #Create a list of referral postcodes to feed into webpage
        postcodes = self.data['Postcode'].tolist()

        ## Sending postcode to website to extract IMD
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.implicitly_wait(15)
        driver.get("https://www.fscbiodiversity.uk/imd/")

        #Selecting the text box for input
        search = driver.find_element("name", "p")

        #create a list for the postcodes, each on a new line
        postcodelist = ""

        for postcode in postcodes:
            postcodelist = postcodelist + postcode + "\r\n"

        # send this postcode list to the webpage
        search.send_keys(postcodelist)

        # select the button element on the page and click it
        search = driver.find_element("xpath", '/html/body/main/form/button')
        search.click()

        #get results
        table = driver.find_element("xpath", '//*[@id="data"]')
        #result = str(search.text)

        # Pulling data from website as pd dataframe
        soup = BeautifulSoup(table.get_attribute('outerHTML'), "html.parser")

        table_headers = []
        for th in soup.find_all('th'):
            table_headers.append(th.text)

        table_data = []
        for row in soup.find_all('tr'):
            columns = row.find_all('td')
            output_row = []
            for column in columns:
                output_row.append(column.text)
            table_data.append(output_row)

        # Save table to a pandas df
        PostcodeIMD = pd.DataFrame(table_data, columns=table_headers)
        # Drop nas
        self.PostcodeIMD = PostcodeIMD.dropna(axis=0).reset_index(drop=True)

        return self.PostcodeIMD



    def summarise_and_save(self, output_prefix, csv_file_path):
        
        self.ConvertPostcodeIMD()

        # make the outputs folder
        if not os.path.exists("Stage1Outputs"):
            os.makedirs("Stage1Outputs")

        ## Merge referral file with IMD file and return it
        self.mergedata = pd.merge(self.data, self.PostcodeIMD, on='Postcode')

        print("Combined1")

        #Merge referral file and LUT to match for ethnicity code
        self.fulldata = pd.merge(self.mergedata, self.Ethnicity_LUT, on='Ethnicity_Code')

        print("Combined2")

        self.modalities = self.fulldata['Modality'].unique()

        print("3")

        summary_table = pd.DataFrame()

        for modality in self.modalities:
               modality_data = self.fulldata[self.fulldata["Modality"] == modality]
            
               print("4")

               #add an age bracket column to data
               modality_data['Age_range'] = pd.cut(modality_data['Age'], 
                                   bins=[0,17,29,39,49,59,69,79,89,90], 
                                   labels=['0-17', '18-29', '30-39',
                                            '40-49', '50-59', '60-69', '70-79', 
                                            '80-89', '90+'])
               

               # count age data based on range
               age_summary = modality_data["Age_range"].value_counts().reset_index()
               age_summary.columns = ["Age_range", "Count"]
               age_summary.to_csv(f"Stage1Outputs/{output_prefix[5:]}_{modality}_age_summary.csv", index=False)
                
                #count referrals by gender of patient
               gender_summary = modality_data["Patient_Gender"].value_counts().reset_index()
               gender_summary.columns = ["Patient_Gender", "Count"]
               gender_summary.to_csv(f"Stage1Outputs/{output_prefix[5:]}_{modality}_gender_summary.csv", index=False)
                
                #count referrals by ethnicity of patient
               ethnicity_summary = modality_data["ETHNIC GROUP"].value_counts().reset_index()
               ethnicity_summary.columns = ["ETHNIC GROUP", "Count"]
               ethnicity_summary.to_csv(f"Stage1Outputs/{output_prefix[5:]}_{modality}_ethnicity_summary.csv", index=False)

                #count referrals by IMD decile of patient
               IMD_summary = modality_data["IMD Decile"].value_counts().reset_index()
               IMD_summary.columns = ["IMD Decile", "Count"]
               IMD_summary.to_csv(f"Stage1Outputs/{output_prefix[5:]}_{modality}_IMD_summary.csv", index=False)

                #count referrals by GP practice of patient
               IMD_summary = modality_data["Patient GP"].value_counts().reset_index()
               IMD_summary.columns = ["Patient GP", "Count"]
               IMD_summary.to_csv(f"Stage1Outputs/{output_prefix[5:]}_{modality}_GPCode_summary.csv", index=False)

        #Write merged data to another file for future use
        self.fulldata.to_csv(f"Stage1Outputs/{output_prefix[5:]}_Merged.csv", index=False)

        print("Complete")





