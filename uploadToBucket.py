#import aws sdk
import boto3

#define accessor
s3 = boto3.resource('s3')

#string array of images to be uploaded
imagesArr = ['/images/image1.jpg', '/images/image2.png', '/images/image3.jpg', '/images/image4.jpg', '/images/image5.jpg']
#index used to help upload the right image to the bucket
index = 1

for image in imagesArr:
  s3.meta.client.upload_file(image, 'cwbuckets2026816', ('image'+index+image[-4:])) # uploads file with a name of image, the image number, and then the image extension
  index++
