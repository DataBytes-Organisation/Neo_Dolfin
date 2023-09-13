import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.stats import norm
from operator import itemgetter
import  csv
import itertools
import datetime

#read input file 
transfile = "neo_dolfin/ai/savings/modified_transactions_data.csv"
df = pd.read_csv(transfile)
print("File read into df")
print(df.head(5))

# Then, resample the DataFrame with daily frequency and forward-fill missing values
def data_resample(df):
    df['postDate'] = pd.to_datetime(df['postDate'])
    df.set_index('postDate', inplace=True)
    df2 = df.resample('D').ffill()
    # Reset the index to have 'postDate' as a regular column again
    print("resampling done.. resting the index")
    df2.reset_index(inplace=True)
    return df2

data= data_resample(df)

# Split the data into train and test
def train_testsplit(df,trainsize):
    df.set_index('postDate', inplace=True)
    train_size = int(len(df) * trainsize)
    traindata = df['balance'][:train_size]
    testdata = df['balance'][train_size:]
    return traindata,testdata

train_data,test_data = train_testsplit(data,0.8)
print("train sample:\n", train_data.head(3))
print("test sample:\n", test_data.head(3))

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
ad_test(train_data)

print("Stationarity check performed.")

def modeltriplets():
    p = d = q = range(0, 2)

    # Generate all different combinations of p, q and q triplets
    pdq = list(itertools.product(p, d, q))

    # Generate all different combinations of seasonal p, q and q triplets
    seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

    print('Examples of parameter combinations for Seasonal ARIMA...')
    print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
    print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
    print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
    return seasonal_pdq,pdq
seasonal_pdq,pdq = modeltriplets()

#vals = pd.DataFrame(columns=["pdq","seasonal_pdq","AIC"])
def get_SARIMAX_Vals(): 
    AIC=[]
    pdqs=[]
    seas_pdq=[]
    for param in pdq:
        for param_seasonal in seasonal_pdq:
            mod = sm.tsa.statespace.SARIMAX(df,
                                                order=param,
                                                seasonal_order=param_seasonal,
                                                enforce_stationarity=True,
                                                enforce_invertibility=False)

            results = mod.fit()
            pdqs.append(param)
            seas_pdq.append(param_seasonal)
            AIC.append(results.aic)
            print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
    return pdqs,seas_pdq,AIC
pdq_param,seas_pdq_param,AIC = get_SARIMAX_Vals() 

params = pd.DataFrame(list(zip(pdq_param, seas_pdq_param,AIC)), columns =['pdq', 'seas_pdq','AIC']) 
#print(params) 
#print("minimum AIC:", min(params.AIC))

def findbestpdq(params):
    params = params.sort_values(by='AIC', ascending=True)
    print("sorted parameters by AIC:", params)
    pdq_fit = params['pdq'].iloc[0]
    spdq_fit = params['seas_pdq'].iloc[1]
    #min_p = params['AIC'].min()
    print("pdq value", pdq_fit)
    print("seasonal values", spdq_fit)
    return pdq_fit,spdq_fit

pdqfit, spdqfit = findbestpdq(params)

def modelfit(pdqfit, spdqfit):
    mod = sm.tsa.statespace.SARIMAX(train_data,
                                order=pdqfit,
                                seasonal_order= spdqfit,
                                enforce_stationarity=False,
                                enforce_invertibility=False)

    results = mod.fit()
    print(results.summary().tables[1])
    return results

  

def drawPredictions():
    results = modelfit(pdqfit,spdqfit)  
    current = datetime.date.today() 
    start= current - datetime.timedelta(days=180)
    end = current + datetime.timedelta(days=180)
    pred = results.get_prediction(start=pd.to_datetime(start),end=pd.to_datetime(end), dynamic=False)
    pred_ci = pred.conf_int()
    print(pred_ci)
    return pred

def plotPredictedBal():
    pred = drawPredictions()
    pred.predicted_mean.plot( label='One-step ahead Forecast', alpha=.7)
    plt.legend()
    plt.show()
plotPredictedBal()