import boto3

#s3_resource = boto3.resource('s3')
session = boto3.Session( 
         aws_access_key_id='AKIA5HWF4LGQVFO37AW5', 
         aws_secret_access_key='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')

print("After boto3 session is configured......")
#Then use the session to get the resource
s3 = session.resource('s3') 

my_bucket = s3.Bucket('elasticbeanstalk-ap-southeast-2-909874321825')
print("before for loop..")
for my_bucket_object in my_bucket.objects.all():
    print(my_bucket_object.key)

for objects in my_bucket.objects.filter(Prefix="Test_S3/"):
    print("csvs: ", objects.key)

obj = s3.Object('elasticbeanstalk-ap-southeast-2-909874321825', 'Test_S3/dummies.csv')
body = obj.get()['Body'].read()
print(body)

"""response = client.get_object(
    Bucket='string',
    IfMatch='string',
    IfModifiedSince=datetime(2015, 1, 1),
    IfNoneMatch='string',
    IfUnmodifiedSince=datetime(2015, 1, 1),
    Key='string',
    Range='string',
    ResponseCacheControl='string',
    ResponseContentDisposition='string',
    ResponseContentEncoding='string',
    ResponseContentLanguage='string',
    ResponseContentType='string',
    ResponseExpires=datetime(2015, 1, 1),
    VersionId='string',
    SSECustomerAlgorithm='string',
    SSECustomerKey='string',
    RequestPayer='requester',
    PartNumber=123,
    ExpectedBucketOwner='string',
    ChecksumMode='ENABLED'
)    """