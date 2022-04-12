from decimal import Decimal # used to round confidence value
import json # used to help parse the lambda event
import boto3 # aws sdk

dynamodb_table = boto3.resource("dynamodb").Table("Imagess2026816") #access table
rekognition = boto3.client("rekognition", "us-east-1") #access rekognition api


def lambda_handler(event, context):
    try:
        for record in event['Records']:
            #lines 13 - 16 parse the information passed to lambda so the bucket and image name may be obtained - was not possible to directly access these values as the json would be returned as string literal sometimes
            body_str = record["body"]
            body_obj = json.loads(body_str)
            body_message = json.loads(body_obj["Message"])
            body_records = json.loads(json.dumps(body_message["Records"]))
            bucket = body_records[0]["s3"]["bucket"]["name"]
            image = body_records[0]["s3"]["object"]["key"]

            response = rekognition.detect_labels( #detect labels in images and store them
                Image={
                    "S3Object": {
                        "Bucket": bucket,
                        "Name": image,
                    }
                },
                MaxLabels=5,
                MinConfidence=85,
            )

            labels = response.get('Labels', None) #get labels from detect_labels response
            #initialise label and label confidence arrays
            labelList = []
            labelConfidence = []

            for label in labels: # populate label and label confidence arrays
                labelList.append(label['Name'])
                labelConfidence.append(Decimal(label['Confidence']))

            dynamodb_table.put_item(Item={ #store image name, labels, and label confidences in dynamodb table
                "ImageName": image,
                "Labels": labelList,
                "Confidence": labelConfidence
            })

    except Exception as e:
        print("An error occurred! See details below.")
        print(e)

