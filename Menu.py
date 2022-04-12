#imports
import boto3  # aws sdk
# used to handle if resource name taken
from botocore.exceptions import ClientError
import os  # used to clear console
import time  # used to pause program temporarily
import json  # used to convert json to string literal

#global variables
# to be appended to the end of every resource created as per spec requirement
student_id = "s2026816"
# defined globally as used in 2 functions
s3_client = boto3.client('s3')
sns_client = boto3.client('sns', region_name='us-east-1')
sqs_client = boto3.client('sqs', region_name='us-east-1')

#function to display menu options

def menu_options():
    os.system('cls' if os.name == 'nt' else 'clear')  # clears console
    print("Enter a number which corresponds with what you want to do:\n----------------------------------------------------\n")
    print("1. Create instance")
    print("2. Create bucket")
    print("3. Create database")
    print("4. Create queue")
    print("5. Create SNS topic")
    print("6. Configure queue Lambda trigger")
    print("7. Exit program\n")

    choice = input("My choice is: ")
    menu(choice)

#exit application or call method based on user choice and take name for resource to pass to relevant method - display menu options once resource created or invalid option selected


def menu(choice):
    if choice == "1":
        instance_name = input("\nWhat would you like to name your instance?\n>>> ")
        create_instance(instance_name)
        # give users 2 seconds to read any output before it is cleared and menu_options is called again
        time.sleep(2)
        menu_options()
    elif choice == "2":
        bucket_name = input("What would you like to call your bucket?\n>>> ")
        create_bucket(bucket_name)
        time.sleep(2)
        menu_options()
    elif choice == "3":
        db_name = input("What would you like to call your database?\n>>> ")
        create_database(db_name)
        time.sleep(2)
        menu_options()
    elif choice == "4":
        q_name = input("What would you like to call your queue?\n>>> ")
        create_queue(q_name)
        time.sleep(2)
        menu_options()
    elif choice == "5":
        sns_name = input("What would you like to call your topic?\n>>> ")
        create_sns(sns_name)
        time.sleep(2)
        menu_options()
    elif choice == "6":
        queue_name = input(
            "What is the name of the queue you'd like to add a Lambda trigger to?\n>>> ")
        create_trigger(queue_name)
        time.sleep(2)
        menu_options()
    elif choice == "7":
        print("Exiting program...")
        exit()
    else:
        print("Please select a valid option! Displaying menu options again...\n")
        time.sleep(2)
        menu_options()


def create_instance(name):
    #create EC2 instance
    print("Instance will be called: " + name+student_id)
    print("Creating...")
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    try:  # to create the instance
        #instance creation
        userData='''#!/bin/bash
                    sudo yum install git -y
                    sudo pip3 install boto3'''

        ec2_client.run_instances(
            ImageId="ami-0c02fb55956c7d316",
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            KeyName="vockey",
            IamInstanceProfile={  # define instance access permissions
                'Arn': 'arn:aws:iam::769750445903:instance-profile/LabInstanceProfile'
            },
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': name+student_id
                        },
                    ]
                },
            ],
            #install git and boto3 on instance
            UserData=userData
        )

        print("Instance created. Returning to menu...")
    except ClientError as e:
        #if instance with name exists
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("Instance already exists")
            name = input("Provide a new unique name for your instance: \n>>>")
            create_instance(name)
        else:
            print("Unexpected error: %s" % e)
            input("Press any key to continue...")
            menu_options()
    except Exception as e:  # handle any other error and return user to menu when ready
        print("Unexpected error: %s" % e)
        input("Press any key to continue...")
        menu_options()


def create_bucket(name):
    print("Bucket will be called: " + name+student_id)
    print("Creating...")
    #Create bucket
    try:  # to create the bucket
        s3_client.create_bucket(
            Bucket=name+student_id
        )
        # Retrieve waiter instance that will wait till a specified bucket exists
        s3_bucket_exists_waiter = s3_client.get_waiter('bucket_exists')
        #wait for bucket to exist
        s3_bucket_exists_waiter.wait(Bucket=name+student_id)

        print("Bucket created. Returning to menu...")

    except ClientError as e:
        #if bucket with name exists
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("Bucket already exists")
            name = input("Provide a new unique name for your bucket: \n>>>")
            create_bucket(name)
        else:
            print("Unexpected error: %s" % e)
            input("Press any key to continue...")
            menu_options()
    except Exception as e:  # handle any other error and return user to menu when ready
        print("Unexpected error: %s" % e)
        input("Press any key to continue...")
        menu_options()


def create_sns(name):
    print("Topic will be called: " + (name+student_id))
    print("Creating...")
    #Create topic
    try:  # to create the topic
        #response stored in variable so it is easier to pull topic arn for notification config
        res = sns_client.create_topic(
            Name=name+student_id,
            Attributes={
                'DisplayName': name+student_id
            },
            Tags=[
                {
                    'Key': 'Name',
                    'Value': name+student_id
                },
            ]
        )

        answer = input("Configure bucket notification to topic? Type yes or no\n>>> ")
        
        if answer.lower() == "yes" or answer.lower() == "y":  # if user wishes to configure notifications
            bucket = input("Enter bucket name here: ")

            sns_topic_policy = { #define policy to allow bucket to access topic
                "Id": "s3EventSNS",
                "Version": "2012-10-17",
                "Statement": [
                {
                    "Sid": "s3EventSNSNotification",
                    "Action": [
                    "sns:Publish"
                    ],
                    "Effect": "Allow",
                    "Resource": res['TopicArn'],
                    "Condition": {
                    "ArnLike": {
                        "aws:SourceArn": "arn:aws:s3:::"+bucket
                    }
                    },
                    "Principal": "*"
                }
                ]
            }

            sns_client.set_topic_attributes( #setting the topic policy attribute to the defined policy
                TopicArn=res['TopicArn'],
                AttributeName='Policy',
                AttributeValue=json.dumps(sns_topic_policy)
            )

            print("Configuring notifications to bucket...")
            time.sleep(5)
            #configure notifications from bucket to sns
            s3_client.put_bucket_notification_configuration(
                Bucket=bucket,
                NotificationConfiguration={
                    'TopicConfigurations': [
                        {
                            # takes topic arn stored when topic was created
                            'TopicArn': res['TopicArn'],
                            'Events': [
                                's3:ObjectCreated:*'  # monitor all create events on bucket
                            ]
                        }
                    ]
                }
            )
            print("Topic created. Returning to menu...")
        # if user does not wish to configure notifications
        elif answer.lower() == "no" or answer.lower() == "n":
            print("Topic created. Returning to menu...")
        else:  # if user types any other character or makes a typo
            print("No valid answer given - to configure notifications between the bucket and topic, this will now have to be done via the GUI.")
            print("Topic created. Returning to menu...")

    except ClientError as e:
        #if instance with name exists
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("Topic already exists")
            name = input("Provide a new unique name for your topic: \n>>>")
            create_sns(name)
        else:
            print("Unexpected error: %s" % e)
            input("Press any key to continue...")
            menu_options()
    except Exception as e:  # handle any other error and return user to menu when ready
        print("Unexpected error: %s" % e)
        input("Press any key to continue...")
        menu_options()


def create_database(name):
    print("Database will be called: " + name+student_id)
    print("Creating...")
    client = boto3.client('cloudformation')
    #Create db using cloudformation template
    try:  # to create the database using a cloudformation template
        #json.dumps to covert from json format to string literal
        stack = input("Provide a stack name: \n>>> ")
        client.create_stack(
            StackName=stack+student_id,
            TemplateBody=json.dumps({
                "Resources": {
                    "MyDatabase": {
                        "Type": "AWS::DynamoDB::Table",
                        "Properties": {
                                "TableName": name+student_id,
                                "AttributeDefinitions": [  # define single attribute as per spec
                                    {
                                        "AttributeName": "ImageName",
                                        "AttributeType": "S"
                                    }
                                ],
                            "KeySchema": [  # define this attribute as the primary partition as per spec
                                    {
                                        "AttributeName": "ImageName",
                                        "KeyType": "HASH"
                                    }
                                ],
                            "ProvisionedThroughput": {
                                    "ReadCapacityUnits": "5",
                                    "WriteCapacityUnits": "5"
                                }
                        },
                    },
                }
            }
            )
        )
        print("Table created using CloudFormation. Returning to menu...")
    except ClientError as e:
        #if db with name exists
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("Database already exists")
            name = input("Provide a new unique name for your database: \n>>>")
            create_database(name)
        else:
            print("Unexpected error: %s" % e)
            input("Press any key to continue...")
            menu_options()
    except Exception as e:  # handle any other error and return user to menu when ready
        print("Unexpected error: %s" % e)
        input("Press any key to continue...")
        menu_options()


def create_queue(name):
    print("Queue will be called: " + name+student_id)
    print("Creating...")
    client = boto3.client('cloudformation')
    #create queue using cloudformation template
    try:  # to create the queue using a cloudformation template and subscribe to SNS topic
        #json.dumps to covert from json format to string literal
        stack = input("Provide a stack name: \n>>> ")

        client.create_stack(
            StackName=stack+student_id,
            TemplateBody=json.dumps({
                "Resources": {
                    "MyQueue": {
                        "Type": "AWS::SQS::Queue",
                        "Properties": {
                                "QueueName": name+student_id,
                        },
                    },
                }
            }
            ),
        )

        answer = input("Subscribe to SNS topic? Type yes or no\n>>> ")
        if answer.lower() == "yes" or answer.lower() == "y":  # if user wants to subscribe to SNS topic

            print("Subscribing to SNS topic...")
            topic = input("Enter topic arn here: ")  # get topic arn

            #get queue url based on name given to create queue
            queue_url = sqs_client.get_queue_url(
                QueueName=name+student_id)['QueueUrl']
            #get queue attributes to allow access of arn
            sqs_queue_attrs = sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['All'])['Attributes']
            #store queue arn
            sqs_queue_arn = sqs_queue_attrs['QueueArn']

            #configure notifications from queue to sns
            sns_client.subscribe(
                TopicArn=topic,
                Protocol='sqs',
                Endpoint=sqs_queue_arn
            )
            print("Queue created using CloudFormation. Returning to menu...")
        elif answer.lower() == "no" or answer.lower() == "n":  # if user does not want to subscribe SNS topic
            print("Queue created using CloudFormation. Returning to menu...")
        else:  # if user enters any other character or makes a typo
            print("No valid answer given - to subscribe to the SNS topic, this will now have to be done via the GUI.")
            print("Queue created using CloudFormation.. Returning to menu...")

    except ClientError as e:
        #if queue with name exists
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("Queue already exists")
            name = input("Provide a new unique name for your queue: \n>>>")
            create_queue(name)
        else:
            print("Unexpected error: %s" % e)
            input("Press any key to continue...")
            menu_options()

    except Exception as e:  # handle any other error and return user to menu when ready
        print("Unexpected error: %s" % e)
        input("Press any key to continue...")
        menu_options()


def create_trigger(queue_name):
    try:
        client = boto3.client('lambda', region_name='us-east-1')
        print("Creating Lambda trigger...")
        lambdaName = input("Enter the name of the Lambda function to add as trigger.\n>>> ")
        #get queue url based on name given to create queue
        queue_url = sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']
        #get queue attributes to allow access of arn
        sqs_queue_attrs = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['All'])['Attributes']
        #store queue arn
        sqs_queue_arn = sqs_queue_attrs['QueueArn']

        #create trigger
        client.create_event_source_mapping(
            EventSourceArn=sqs_queue_arn,
            FunctionName=lambdaName,
            Enabled=True,
            BatchSize=10
        )
        
        print("Lambda trigger created. Returning to menu...")
    except ClientError as e:
        #if trigger exists
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("Trigger already exists")
            input("Press any key to continue...")
        else:
            print("Unexpected error: %s" % e)
            input("Press any key to continue...")
            menu_options()
    except Exception as e:  # handle any other error and return user to menu when ready
        print("Unexpected error: %s" % e)
        input("Press any key to continue...")
        menu_options()


menu_options()  # run menu_options once all methods have been defined
