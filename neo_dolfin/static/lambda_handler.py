import json
import boto3
from io import StringIO
import pandas as pd
import requests
import numpy as np


s3_client = boto3.client('s3')

bucket_name = "neodolfin-transaction-data-storage-01"
destination_bucket_name = "neodolfin-transaction-data-storage-01-processed"
''' 
This file contains the code for the raw data processing lambda function. It will need to be applied to the Dolfin AWS account whenever we are ready for that. 
We also need to add a trigger, which will be S3 Put and Post Events for the raw data s3 bucket.
The prefix is currently "raw_data_" and the suffic is ".csv", both of which can be changed
in the app.py code if deemed necessary, then those values can be added to the Event config.
See Dolfin Lambda Function Document for further details
'''




def lambda_handler(event, context):
    '''
    Process raw data from basiq into a more useful format. Based on code suggestions in task card as well as code/idea from trimester 1
    '''

    object_name = event['Records'][0]["s3"]["object"]["key"]
    new_name = object_name.split('.')[0]

    # Found this way to get around errors I was encountering with dataframe data type https://stackoverflow.com/questions/47379476/how-to-convert-bytes-data-into-a-python-pandas-dataframe, adapted for our use
    df_csv = s3_client.get_object(Bucket = bucket_name, Key = object_name)
    data_bytes = str(df_csv['Body'].read(), 'utf-8')
    data_transform = StringIO(data_bytes)
    
    # Changed original to match the SavingsPredAI.ipynb file
    df = pd.read_csv(data_transform)
    
    df["postDate"] = df["postDate"].str.replace("Z", "")
    df["postDate"] = pd.to_datetime(df["postDate"], format="%Y-%m-%dT%H:%M:%S")
    columns_to_keep = ["postDate", "balance"]
    df = df[columns_to_keep]
    df['postDate'] = pd.to_datetime(df['postDate']).dt.date
    df = df.groupby('postDate').agg({'balance': 'min'}).reset_index()
    df.set_index('postDate', inplace=True)

    df.reset_index(inplace=True)
    
    # Used idea from https://stackoverflow.com/questions/38154040/save-dataframe-to-csv-directly-to-s3-python and adapted for our dataframe
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3')
    s3_resource.Object(destination_bucket_name, new_name + ".csv").put(Body=csv_buffer.getvalue())
    
    return {
        'statusCode': 200,
        'body': json.dumps(csv_buffer.getvalue())
    }

'''
Could create a layer with Basiq service and requests imported in order to get account information
'''