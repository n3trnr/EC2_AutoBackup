import boto3, json, ec2_backup, ec2_delete
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    command = event['command']
    if command == 'Backup':
        ec2_backup.backup_ami()
    elif command == 'Delete':
        ec2_delete.delete_ami()
    
