import json # used to help parse the lambda event
import boto3 # aws sdk

rekognition = boto3.client("rekognition", "us-east-1") #access rekognition api
sns = boto3.client('sns') #access sns to send text

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            #lines 12 - 15 parse the information passed to lambda so the bucket and image name may be obtained - was not possible to directly access these values as the json would be returned as string literal sometimes
            body_str = record["body"]
            body_obj = json.loads(body_str)
            body_message = json.loads(body_obj["Message"])
            body_records = json.loads(json.dumps(body_message["Records"]))
            bucket = body_records[0]["s3"]["bucket"]["name"]
            image = body_records[0]["s3"]["object"]["key"]

            response = rekognition.detect_protective_equipment( #detect and store if PPE (face and hand coverings) is detect
                Image={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': image,
                    }
                },
                SummarizationAttributes={
                    'MinConfidence': 85, # to be added to PersonsWithRequiredEquipment list, the confidence must be 85 or more
                    'RequiredEquipmentTypes': [
                        'FACE_COVER',
                        'HAND_COVER',
                    ]
                }
            )

            if len(response['Summary']['PersonsWithoutRequiredEquipment']) > 0: #if there are entries in the PersonsWithoutRequiredEquipment list in the detection response, send an sms message
                sns.publish(
                    PhoneNumber='+ZZ-ZZZZZZZZZZ',
                    Message='PPE not adhered to in ' + image
                )
    except Exception as e:
        print("An error occurred! See details below.")
        print(e)
