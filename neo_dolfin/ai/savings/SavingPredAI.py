import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.stats import norm
from operator import itemgetter
import csv
import itertools
import datetime
import SavingPredAIUtil as util

#read input file 
transfile = "neo_dolfin/static/data/modified_transactions_data.csv"
df = util.read_file(path = transfile )

#resample the DataFrame with daily frequency and forward-fill missing values
data= util.data_resample(df)

# Split the data into train and test
train_data,test_data = util.train_testsplit(data,0.8)
print("train sample:\n", train_data.head(3))
print("test sample:\n", test_data.head(3))

# checking stationarity
util.ad_test(train_data) 

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
    #print(pred_ci)
    #print(pred.predicted_mean)
    pred_mean = pd.DataFrame(pred.predicted_mean)
    pred_ci['mean_balance'] = pred_mean
    predtrans_file = "neo_dolfin/static/Predicted_Balances.csv"
    pred_ci.to_csv(predtrans_file, sep='\t')
    return pred