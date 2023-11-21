import pandas as pd
from statsmodels.tsa.stattools import adfuller

#read input file 
def read_file(path):
    df = pd.read_csv(path)
    print("File read into df")
    print(df.head(10))
    return df 

# Then, resample the DataFrame with daily frequency and forward-fill missing values
def data_resample(df):
    df['postDate'] = pd.to_datetime(df['postDate'])
    df.set_index('postDate', inplace=True)
    df2 = df.resample('D').ffill()
    # Reset the index to have 'postDate' as a regular column again
    print("resampling done.. resting the index")
    df2.reset_index(inplace=True)
    return df2

# Split the data into train and test
def train_testsplit(df,trainsize):
    df.set_index('postDate', inplace=True)
    train_size = int(len(df) * trainsize)
    traindata = df['balance'][:train_size]
    testdata = df['balance'][train_size:]
    return traindata,testdata 

# checking stationarity
def ad_test(dataset):
     dftest = adfuller(dataset, autolag = 'AIC')
     print("1. ADF : ",dftest[0])
     print("2. P-Value : ", dftest[1])
     print("3. Num Of Lags : ", dftest[2])
     print("4. Num Of Observations Used For ADF Regression:",      dftest[3])
     print("5. Critical Values :")
     for key, val in dftest[4].items():
         print("\t",key, ": ", val)
     if (dftest[1] > 0.05):
        print("Data is not stationary") #if p>0.05; Data is not stationary
     print("Data is stationary")   


  