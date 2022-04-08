#import aws sdk
import boto3
#import module to allow sleep
import time
import logging
from botocore.exceptions import ClientError
import json #used to convert json to string literal

#define accessor
s3 = boto3.resource('s3')
sns_client = boto3.client('sns', 'us-east-1')

#string array of images to be uploaded
imagesArr = ['./images/image1.jpg', './images/image2.png', './images/image3.jpg', './images/image4.jpg', './images/image5.jpg']
#index used to help upload the right image to the bucket
index = 1

for image in imagesArr:
  # copies file string from images array and uploads it to S3 Bucket with a name of image, the image number, and then the image extension
  s3.meta.client.upload_file(image, 'mycloudtopics2026816', ('image'+str(index)+image[-4:])) 
  time.sleep(30) #uploads file in 30s intervals
  if index != 5:
    print("File uploaded. Uploading next file...")
  else:
    print("All files uploaded")
  
  index+=1
