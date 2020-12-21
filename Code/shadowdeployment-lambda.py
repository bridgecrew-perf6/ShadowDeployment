import os
import io
import boto3
import json
import csv
import sys
import uuid
from urllib.parse import unquote_plus

# grab environment variables
ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
ENDPOINT_NAME1 = os.environ['ENDPOINT_NAME1']
BUCKET = os.environ['BUCKET']
runtime= boto3.client('runtime.sagemaker')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    data = json.loads(json.dumps(event))
    payload = data['data']
    print("payload***")
    print(payload)
    
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       ContentType='text/csv',
                                       Body=payload)
    print(response)
    result = json.loads(response['Body'].read().decode())
    print(result)
    pred = int(result['predictions'][0]['score'])
    predicted_label = 'M' if pred == 1 else 'B'
    print("Predicted result- from model version 1",predicted_label)
    response1 = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME1,
                                       ContentType='text/csv',
                                       Body=payload)
    print(response1)
    result1 = json.loads(response1['Body'].read().decode())
    print(result1)
    pred = int(result1['predictions'][0]['score'])
    predicted_label1 = 'M' if pred == 1 else 'B'
    print("Predicted result- from model version 2",predicted_label1)
    requestid=response['ResponseMetadata']['RequestId']
    my_json_string = json.dumps({'RequestID': requestid,'Version1 Response': predicted_label, 'Version2 Response': predicted_label1})
    bodytext=predicted_label+predicted_label1
    filename="shadowdeployment/"+requestid+".json"
    s3.put_object(
     Bucket=BUCKET,
     Key=filename,
     Body=my_json_string
    )
    return predicted_label