import pandas as pd
import numpy as np

# Making new CDC data

original_data = pd.read_csv("CDCReferralDummy2.csv")

larger_data_size = 5000
larger_data = original_data.sample(n=larger_data_size, replace=True)

larger_data.to_csv("CDCReferralDummy.csv", index=False)

# Making new baseline data

original_data = pd.read_csv("ReferralData.csv")

larger_data_size = 3000
larger_data = original_data.sample(n=larger_data_size, replace=True)

larger_data.to_csv("ReferralDummy.csv", index=False)