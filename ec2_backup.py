# Automated AMI Backups
#
#
# This script will search for all instances having a tag with "Backup" or "backup" on it.

import boto3
import collections
import datetime
import sys
import pprint

ec = boto3.client('ec2')
#image = ec.Image('id')

def backup_ami():
    
    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag:AutoBackup', 'Values': ['TRUE']},
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print ("Found %d instances that need backing up" % len(instances))
    print (list)
    # to_tag = collections.defaultdict(instances)
    to_tag = collections.defaultdict(list)
    to_ec2_name = collections.defaultdict(list)
    # print(to_tag)
    for instance in instances:
        try:
            retention_days = [
                int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
        except IndexError:
            retention_days = 10

            #snap = ec.create_snapshot(
            #    VolumeId=vol_id,
            #)
            
            #create_image(instance_id, name, description=None, no_reboot=False, block_device_mapping=None, dry_run=False)
            # DryRun, InstanceId, Name, Description, NoReboot, BlockDeviceMappings
            create_time = datetime.datetime.now()
            create_fmt = create_time.strftime('%Y-%m-%d')
            # create_date = time.strptime(create_fmt, '%Y-%m-%d')      
            AMIid = ec.create_image(InstanceId=instance['InstanceId'], Name="AutoBackup - " + [result['Value'] for result in instance['Tags'] if result['Key'] == 'Name'][0], Description="Lambda created AMI of this EC2 instance : " + instance['InstanceId'] + " from " + create_fmt, NoReboot=True, DryRun=False)
            # print(AMIid)
            # print('--------------------------')
            # print(retention_days)
            # ec.create_tags(
            #     Resources=to_tag[retention_days],
            #     Tags=[
            #         {'Key': 'Name', 'Value': [result['Value'] for result in instance['Tags'] if result['Key'] == 'Name'][0]}
            #         ]
            # )
            
            # pprint.pprint(instance)
            #sys.exit()
            #break
        
            #to_tag[retention_days].append(AMIid)
            
            to_tag[retention_days].append(AMIid['ImageId'])
            to_ec2_name[retention_days].append(instance['InstanceId'])
            print ("Retaining AMI %s of instance %s for %d days" % (
                AMIid['ImageId'],
                instance['InstanceId'],
                retention_days,
            ))

    print (to_tag.keys())
    
    for retention_days in to_tag.keys():
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%Y-%m-%d')
        # del_date = time.strptime(delete_fmt, '%Y-%m-%d')
        test_today = str(datetime.date.today())
        print ("Will delete %d AMIs on %s" % (len(to_tag[retention_days]), delete_fmt))
        print("========================================")
        print(test_today)
        # print(instance['Tags'])
        # inst_name = str([result['Value'] for result in instance['Tags'] if result['Key'] == 'Name'][0]) 
        print(retention_days)
        print(to_tag[retention_days])
        print(to_ec2_name[retention_days])
        print("========================================")
        #break
        
        # ec2_name = ec.describe_instances({'Name': 'Name'})
        # print(ec2_name)
        # for j in to_ec2_name[retention_days]:
        #     print(j)
        ec.create_tags(
            Resources=to_tag[retention_days],
            Tags=[
                # {'Key': 'DeleteOn', 'Value': delete_fmt},
                {'Key': 'CreateOn', 'Value': test_today},
                {'Key': 'DeleteOn', 'Value': delete_fmt},
                # {'Key': 'Name', 'Value': j}
            ]
        )
    
