import boto3
import json

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')

dbTableName = 'autoguard'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
vehiclesTable = dynamodb.Table(dbTableName)

bucket = 'ag-auth-vehicle'

def lambda_handler(event, context):
    print(event)
    key = event['queryStringParameters']['objectKey']
    
    response = rekognition.detect_text(
        Image = {
            'S3Object':
            {
                'Bucket': bucket,
                'Name': key
            }
        }
    )
    
    for r in response['TextDetections']:
        print(r['DetectedText'])

        match = vehiclesTable.get_item(
            Key = {
                'id': r['DetectedText']
            }
        )

        if 'Item' in match:
            print('Authenticated User, ', match['Item'])
            return httpResp(200, {
                'Message': 'Success',
                'Data': {
                    'firstName' : match['Item']['firstName'],
                    'lastName' : match['Item']['lastName'],
                    'parkingNumber' : match['Item']['parkingNumber'],
                }
            })
    print("Couldn't find registration number")
    return httpResp(403, {
        'Message': 'Authentication Failed'
    })
        
def httpResp(code, body = None):
    response = {
        'statusCode': code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response