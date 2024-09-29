import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')

dbTableName = 'autoguard'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
vehiclesTable = dynamodb.Table(dbTableName)

def lambda_handler(event, context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key'] #image name, should be like Shivam_Garg_C20.jpg

    try:
        response = detect_text(bucket, key)
        print(response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            allTexts = response['TextDetections']
            # choose the one with most confidence
            chosenText = max(allTexts, key=lambda x: x['Confidence'])
            regNumber = chosenText['DetectedText']
            personalDetails = key.split('.')[0].split('_')
            firstName = personalDetails[0]
            lastName = personalDetails[1]
            parkingNumber = personalDetails[2]
            registerVehicle(regNumber, firstName, lastName, parkingNumber)
        return response
    except Exception as e:
        print(e)
        print('Error in registration while indexing image {} from bucket {}'.format(key, bucket))
        raise e
    
def detect_text(bucket, key):
    response = rekognition.detect_text(
        Image = {
            'S3Object':
            {
                'Bucket': bucket,
                'Name': key
            }
        }
    )
    return response

def registerVehicle(regNumber, firstName, lastName, parkingNumber):
    vehiclesTable.put_item(
        Item = {
            'id': str(regNumber),
            'firstName': firstName,
            'lastName': lastName,
            'parkingNumber': str(parkingNumber),
        }
    )