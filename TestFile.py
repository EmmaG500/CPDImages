import boto3 #aws sdk

#access aws services
instance = boto3.client("ec2")
s3 = boto3.client("s3")
sns = boto3.client("sns")
queue = boto3.client("sqs")
client = boto3.client('lambda')
cloud = boto3.client("cloudformation")

try:
  print("Listing EC2 instances...\n")
  print(instance.describe_instances())

  print("\nListing buckets...\n")
  print(s3.list_buckets())

  print("\nListing bucket contents...\n")
  bucket = input("Enter bucket name: ")
  print()
  print(s3.list_objects_v2(Bucket=bucket))

  print("\nListing bucket events...\n")
  print(s3.get_bucket_notification_configuration(Bucket=bucket))

  print("\nListing topics...\n")
  print(sns.list_topics())

  print("\nListing subscriptions...\n")
  print(sns.list_subscriptions())

  print("\nListing topic attributes...\n")
  topic = input("Enter topic ARN here: ")
  print()
  print(sns.get_topic_attributes(TopicArn=topic))

  print("\nListing queues...\n")
  queues = queue.list_queues()
  print(queues)

  for q in queues['QueueUrls']:
    print("Listing attributes for " + q +"...\n")
    print(queue.get_queue_attributes(QueueUrl=q))

  print("\nListing Lamba functions...\n")
  functions = client.list_functions()
  print(functions)

  for f in functions['Functions']:
      if f['FunctionName'] != "MainMonitoringFunction" and f['FunctionName'] != "LightsailMonitoringFunction": #ignore these two functions as LabRole does not have perms to access
        print("\nListing details for "+f['FunctionName']+"...\n")
        print(client.list_function_event_invoke_configs(FunctionName=f['FunctionName']))

  print("\nListing CloudFormation stacks...\n")
  print(cloud.list_stacks())
  print("Exiting...")
except Exception as e:
  print("Some or no resources exist! Please create these resources then run the test file again.\n Exiting...")
