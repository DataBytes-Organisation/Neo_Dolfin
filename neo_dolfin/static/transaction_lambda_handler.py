'''
This lambda function can be used to process raw transaction data and return a processed dataframe
that narrows down to more specific data, possibly for use in the dashboard. It differs
from the other lambda in the number of columns it returns, as the other function only returns
postDate and balance.
'''


import json
import boto3
from io import StringIO
import pandas as pd
import requests

s3_client = boto3.client('s3')

bucket_name = "neodolfin-transaction-data-storage-01"
destination_bucket_name = "neodolfin-transaction-data-storage-01-processed"

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
    df = pd.read_csv(data_transform)
    
    # I have decided to keep a couple of these columns as I think direction, status and id could all be useful. If we are certain we want them gone then I am happy to remove them
    data = df.filter(["id", "status", "amount", "direction", "account", "class", "postDate", "subClass.title"], axis=1)
    monthsForProcessing = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # I think this column works as category
    data.rename(columns = {'subClass.title':'category'}, inplace = True)

    #Processing the date value that is returned. It will be split from a string in to 3 arrays listed below
    year = []
    month = []
    day = []
    hour = []
    minute = []
    second = []
    
    #Account name included to give something human readable to the account id number
    accountName = []

    #Here I am transforming the data in the postDate and account columns. 
    for column in df[["postDate"]]:
        for val in df[column]:
            if column == "postDate":
                '''
                postDate needs pre-processing in order to be of use to us in analysing or displaying in the front end. This is accomplished by splitting the
                original date string in half, then splitting those two strings into year, month, day, hour, minute and second strings.
                These are then added to their appropriate arrays and added to the dataframe
                '''
                
                splitTime = val.split('T')
                yearMonthDay = splitTime[0].split("-")
                hourMinuteSecond = splitTime[1].split(":")
            
                year.append(yearMonthDay[0])
                month.append(monthsForProcessing[int(yearMonthDay[1]) - 1])
                day.append(yearMonthDay[2])
                hour.append(hourMinuteSecond[0])
                minute.append(hourMinuteSecond[1])
                second.append(hourMinuteSecond[2][:2])
    
    # Adding the new arrays as columms in the existing dataframe
    data["year"] = year
    data["month"] = month
    data["day"] = day
    data["hour"] = hour
    data["minute"] = minute
    data["second"] = second
    data = data.drop('postDate', axis=1)
    data["category"].fillna("Unknown", inplace = True)

    # Used idea from https://stackoverflow.com/questions/38154040/save-dataframe-to-csv-directly-to-s3-python and adapted for our dataframe
    csv_buffer = StringIO()
    data.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3')
    s3_resource.Object(destination_bucket_name, new_name + ".csv").put(Body=csv_buffer.getvalue())
    
    return {
        'statusCode': 200,
        'body': json.dumps(csv_buffer.getvalue())
    }

'''
Could create a layer with Basiq service and requests imported in order to get account information
'''