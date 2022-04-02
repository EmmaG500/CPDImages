#import aws sdk
import boto3
#import module to allow sleep
import time
import logging

#define accessor
s3 = boto3.resource('s3')
sns_client = boto3.client('sns')

#string array of images to be uploaded
imagesArr = ['./images/image1.jpg', './images/image2.png', './images/image3.jpg', './images/image4.jpg', './images/image5.jpg']
#index used to help upload the right image to the bucket
index = 1

for image in imagesArr:
  # copies file string from images array and uploads it to S3 Bucket with a name of image, the image number, and then the image extension
  s3.meta.client.upload_file(image, 'letsdothiss2026816', ('image'+str(index)+image[-4:])) 
  index+=1
  time.sleep(30) #uploads file in 30s intervals
  publish_message('snsName', 'File Uploaded', 'str')
  if index != 5:
    print("File uploaded. Uploading next file...")
  else:
    print("All files uploaded")
    
  
def publish_message(topic, message, attributes):
        """
        Publishes a message, with attributes, to a topic. Subscriptions can be filtered
        based on message attributes so that a subscription receives messages only
        when specified attributes are present.

        :param topic: The topic to publish to.
        :param message: The message to publish.
        :param attributes: The key-value attributes to attach to the message. Values
                           must be either `str` or `bytes`.
        :return: The ID of the message.
        """
        try:
            att_dict = {}
            for key, value in attributes.items():
                if isinstance(value, str):
                    att_dict[key] = {'DataType': 'String', 'StringValue': value}
                elif isinstance(value, bytes):
                    att_dict[key] = {'DataType': 'Binary', 'BinaryValue': value}
            response = topic.publish(Message=message, MessageAttributes=att_dict)
            message_id = response['MessageId']
            logger.info(
                "Published message with attributes %s to topic %s.", attributes,
                topic.arn)
        except ClientError:
            logger.exception("Couldn't publish message to topic %s.", topic.arn)
            raise
        else:
            return message_id
