#pip install selenium
#pip install chromedriver-binary
#pip3 install webdriver-manager
# from selenium import webdriver
# import chromedriver_binary  # Adds chromedriver binary to path
#pip install selenium pandas beautifulsoup4

#Set wd
#os.chdir("yourpath")

import pandas as pd
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# to replace once part of wider code
csv_file = "CDCReferralDummy.csv"

#Pull in list of postcodes
ReferralFile = pd.read_csv(csv_file)
postcodes = ReferralFile['Postcode'].tolist()

## Sending postcode to website to extract IMD
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.implicitly_wait(15)
driver.get("https://www.fscbiodiversity.uk/imd/")

search = driver.find_element("name", "p")

postcodelist = ""

for postcode in postcodes:
     postcodelist = postcodelist + postcode + "\r\n"

search.send_keys(postcodelist)

#Find the button
search = driver.find_element("xpath", '/html/body/main/form/button')

#Click it
search.click()

#Find results table
table = driver.find_element("xpath", '//*[@id="data"]')

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
PostcodeIMD = PostcodeIMD.dropna(axis=0).reset_index(drop=True)

## Merge referral file with IMD file and return it
data = pd.merge(ReferralFile, PostcodeIMD, on='Postcode')

