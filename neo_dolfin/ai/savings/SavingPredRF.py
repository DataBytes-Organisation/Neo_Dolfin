import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import SavingPredAIUtil as util

#read input file 
transfile = "neo_dolfin/static/data/modified_transactions_data.csv"
df = util.read_file(path = transfile )

#resample the DataFrame with daily frequency and forward-fill missing values
data= util.data_resample(df)

# Split the data into train and test
train_data,test_data = util.train_testsplit(data,0.8)
print("train sample:\n", train_data.head(10))
print("test sample:\n", test_data.head(10))

