import boto3

client = boto3.client('events',
                        region_name='ap-southeast-2'
                        aws_access_key_id='AKIA5HWF4LGQVFO37AW5', 
                        aws_secret_access_key='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'))

detailjson ='{ "Error": "SQL Time out", "file": "App.log", "timestamp": "2023-09-07 23:10:30" }'
response = client.put_events(
    Entries=[ { 'Source': 'applog',
                'DetailType': 'user log',
                'Detail': detailjson,
                'EventBusName': 'Dolfineventlogbus'
                }
            ]
)

print(response)