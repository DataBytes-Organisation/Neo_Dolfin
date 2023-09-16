import boto3

s3 = boto3.client('s3')
bucket_name="test-bucket-neodolfin-123"

def test_create_bucket():
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-2'})
    session = boto3.session.Session()
    s3_resource = session.resource('s3')
    resp = s3_resource.meta.client.head_bucket(Bucket=bucket_name)
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

def test_delete_bucket():
    resp = s3.delete_bucket(Bucket = bucket_name)
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 204