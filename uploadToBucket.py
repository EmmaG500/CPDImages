#import aws sdk
import boto3
#import module to allow sleep
import time
#used to access images directory
import os 

#define accessor
s3 = boto3.resource('s3')
sns_client = boto3.client('sns', 'us-east-1')

try: #to initialise the images array
    #string array of images to be uploaded - array is populated with images found in the directory named Images on EC2 Instance
    print(os.listdir("./images"))
    imagesArr = os.listdir("./images")
    #index used to help upload the right image to the bucket
    index = 1

    try: #to upload the contents of the images array to the s3 bucket
        print("Uploading files...") #indicate that function has started and files will start getting uploaded to S3 bucker
        for image in imagesArr:
            # copies file string from images array and uploads it to S3 Bucket with a name of image, the image number, and then the image extension
            s3.meta.client.upload_file(image, 'imagesbuckets2026816', ('image'+str(index)+image[-4:])) 
            time.sleep(30) #uploads file in 30s intervals
            if index != 5: #print message to indicate that the function is not finished
                print("File uploaded. Uploading next file...")
            else: #print message to indicate function is done
                print("All files uploaded. Exiting...")
            
            index+=1 #increment index by 1 to allow for the correct message to be printed in the next loop

    except Exception as e: #when an issue occurs in the loop, print error message to console for further debugging
        print("An error occurred! See below for more information")
        print(e)

except Exception as e: #when an issue occurs initialising the images array, print error message to console for further debugging
        print("An error occurred! See below for more information")
        print(e)
