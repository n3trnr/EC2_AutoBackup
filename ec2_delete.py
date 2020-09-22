
import boto3
import collections
import datetime
import time
import sys

ec = boto3.client('ec2')
ec2 = boto3.resource('ec2')
images = ec2.images.filter(Owners=["self"])

def delete_ami():

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

    print ("Found %d instances that need evaluated" % len(instances))

    to_tag = collections.defaultdict(list)

    imagesList = []

    imagecount = 0
    # Loop through all of our instances with a tag named "Backup"
    for instance in instances:

        # Loop through each image of our current instance
        for image in images:

            # Our other Lambda Function names its AMIs Lambda - i-instancenumber.
            # We now know these images are auto created
            if image.name.startswith('AutoBackup - '):
                today_date = datetime.date.today()
                today_fmt = today_date.strftime('%Y-%m-%d')
                today_time = time.strptime(today_fmt, '%Y-%m-%d')

                try:
                    if image.tags is not None:
                        for t in image.tags:
                            if t['Key'] == 'DeleteOn':
                                imagecount = imagecount + 1
                                deletion_date = t.get('Value')
                                print(deletion_date)
                                delete_date = time.strptime(deletion_date, "%Y-%m-%d")
                                print("DeleteDate : ")
                                print(delete_date)
                                print("TodayDate : ", today_date)
                                print("todaytime")
                                print(today_time)
                                
                                # If image's DeleteOn date is less than or equal to today,
                                # add this image to our list of images to process later
                                if delete_date <= today_time:
                                    imagesList.append(image.id)
                except IndexError:
                    deletion_date = False
                    delete_date = False

        print ("instance " + [result['Value'] for result in instance['Tags'] if result['Key'] == 'Name'][0] + " has " + str(imagecount) + " AMIs")

    print ("=============")
    print ("About to process the following AMIs:")
    print (imagesList)

    myAccount = boto3.client('sts').get_caller_identity()['Account']
    snapshots = ec.describe_snapshots(MaxResults=1000, OwnerIds=[myAccount])['Snapshots']

    # loop through list of image IDs
    for image in imagesList:
        print ("deregistering image %s" % image)
        amiResponse = ec.deregister_image(
            DryRun=False,
            ImageId=image,
        )

        for snapshot in snapshots:
            if snapshot['Description'].find(image) > 0:
                snap = ec.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                print ("Deleting snapshot " + snapshot['SnapshotId'])
                print ("-------------")
