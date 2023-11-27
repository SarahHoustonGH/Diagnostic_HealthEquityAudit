import pandas as pd
import numpy as np

# Making new CDC data

#Read in the data
original_data = pd.read_csv("CDCReferralDummy2.csv")

##Set the size (row numbers) required
larger_data_size = 5000

## Randomly sample rows for new dataset
larger_data = original_data.sample(n=larger_data_size, replace=True)

##Write dataset
larger_data.to_csv("CDCReferralDummy.csv", index=False)

# Making new baseline data
original_data = pd.read_csv("ReferralData.csv")

##Set the size (row numbers) required 
larger_data_size = 3000

## Randomly sample rows for new dataset
larger_data = original_data.sample(n=larger_data_size, replace=True)

##Write dataset
larger_data.to_csv("ReferralDummy.csv", index=False)