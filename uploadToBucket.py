#import aws sdk
import boto3
#import module to allow sleep
import time
#used to access images directory
import os
#used to access current time to print to console
from datetime import datetime

#define accessor
s3 = boto3.resource('s3')
sns_client = boto3.client('sns', 'us-east-1')

try: #to initialise the images array
    #string array of images to be uploaded - array is populated with images found in the directory named Images on EC2 Instance
    print(os.listdir("./images"))
    imagesArr = []
    for file in os.listdir("./images"):
        imagesArr.append("./images/"+file)
    #index used to help upload the right image to the bucket
    index = 1

    try: #to upload the contents of the images array to the s3 bucket
        print("Uploading files...") #indicate that function has started and files will start getting uploaded to S3 bucker
        for image in imagesArr:
            now = datetime.now() #capture current time
            current_time = now.strftime("%H:%M:%S") #format current time
            # copies file string from images array and uploads it to S3 Bucket with a name of image, the image number, and then the image extension
            s3.meta.client.upload_file(image, 'imagesbuckets2026816', ('image'+str(index)+image[-4:])) 
            time.sleep(30) #uploads file in 30s intervals
            #print message to indicate that the function is still running with the time the file was uploaded
            print(current_time + ": File uploaded. Uploading next file...") 
            if index == 5: #print message to indicate function is done
                print("All files uploaded. Exiting...")
            
            index+=1 #increment index by 1 to allow for the correct message to be printed in the next loop

    except Exception as e: #when an issue occurs in the loop, print error message to console for further debugging
        print("An error occurred when trying to upload the files! See below for more information")
        print(e)

except Exception as e: #when an issue occurs initialising the images array, print error message to console for further debugging
        print("An error occurredwhen trying to access the directory! See below for more information")
        print(e)
