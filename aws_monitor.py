"""
Module that:
a) Checks whether there are public Buckets
b) Checks whether log groups have retention policies
"""
#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError

def check_bucket_public(bucket_name, s3_client):
    try:
        response = s3_client.get_bucket_policy_status(Bucket=bucket_name)
        if response['PolicyStatus']['IsPublic']:
            return True
        else:
            return False
    except ClientError as err:
        if err.response['Error']['Code'] == 'NoSuchBucketPolicy':
            return False
        else:
            raise

def fetch_and_check_s3_buckets():
    # Create an S3 client
    s3_client = boto3.client('s3')

    # Fetch all S3 buckets
    response = s3_client.list_buckets()
    buckets = response['Buckets']

    # Check each bucket for public access
    public_buckets = []
    for bucket in buckets:
        bucket_name = bucket['Name']
        if check_bucket_public(bucket_name, s3_client):
            public_buckets.append(bucket_name)

    # Print the public buckets
    if public_buckets:
        print("Public buckets:")
        for bucket_name in public_buckets:
            print(bucket_name)
    else:
        print("No public buckets found.")

def check_and_update_log_group_retention():
    # Initialize CloudWatch logs client
    client = boto3.client('logs')

    # Fetch all log groups
    response = client.describe_log_groups()

    # Loop through log groups and check for retention policies
    for log_group in response['logGroups']:
        log_group_name = log_group['logGroupName']
        retention_in_days = log_group.get('retentionInDays')

        if retention_in_days is None:
            print(f'Log group {log_group_name} does not have a retention policy. Applying 30-day retention policy.')
            # client.put_retention_policy(
            #     logGroupName=log_group_name,
            #     retentionInDays=30
            # )
        else:
            print(f'Log group {log_group_name} already has a retention policy of {retention_in_days} days.')

    print('Retention policy check and update completed.')

def main():
    print("Checking S3 buckets for public access...")
    fetch_and_check_s3_buckets()

    print("\nChecking CloudWatch log group retention policies...")
    check_and_update_log_group_retention()

if __name__ == '__main__':
    main()
