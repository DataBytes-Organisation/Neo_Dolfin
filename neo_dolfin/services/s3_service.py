import boto3
import datetime
from asgiref.sync import sync_to_async
import aioboto3
import asyncio
import os 

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

class S3Service():
    ''' This is a service for getting objects from an S3 Bucket, with the option to get a specific object
        or to get the last modified'''

    async def set_object(self, bucket_name, object_name, object_bytes):
        session = aioboto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)

        async with session.resource("s3") as s3:
            bucket = await s3.Bucket(bucket_name)
            response = await bucket.put_object(Body = object_bytes, Key = object_name)
            return response


    async def get_specified_object(bucket_name, object_name):
        session = aioboto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)

        async with session.resource("s3") as s3:
            bucket = await s3.Bucket(bucket_name)
            target_object = await bucket.Object(key = object_name)
            target_object_get = await obj.get()

            return await target_object_get['Body'].read()


    # def set_object(data, bucket_name, username, file_extension):
    #     # Creates a new object, combining the user's username, the current time and the file extension to provide a unique filename
    #     s3_client = boto3.client('s3')
    #     current_time = datetime.datetime.now().strftime("%m%d%Y%H%M%S")

    #     response = s3_client.put_object(Body = data, Bucket = bucket_name, Key = username + current_time + file_extension)

    #     return response['HTTPStatusCode']
    
    async def get_latest_object(bucket_name, username):
        session = aioboto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)
        objects = []
        async with session.resource("s3") as s3:
            bucket = await s3.Bucket(bucket_name)
            x = bucket.objects.filter(Prefix=username)
            async for y in x:
                obj.append(y)

            return objects

    def create_bucket(bucket_name, configuration_json = None):
        # This method has many more properties that we can set. Worth discussing the merit of including these in our implementation
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html
        s3 = boto3.client('s3')

        response = s3.create_bucket(Bucket = bucket_name, CreateBucketConfiguration = configuration_json)

        return response['HttpStatusCode']

    def delete_bucket(bucket_name):
        # Delete a specific s3 bucket
        s3 = boto3.client('s3')

        response = s3.delete_bucket(Bucket = bucket_name)

        return response['HttpStatusCode']
