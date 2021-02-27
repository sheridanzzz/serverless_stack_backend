import json
import boto3
from boto3.dynamodb.conditions import Key,Attr


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Url-Tags')



def lambda_handler(event, context):
    # TODO implement
    
    taglist = []
    
    
    if(event['httpMethod'])=='GET':
        for tag in event['queryStringParameters']:
            taglist.append(event['queryStringParameters'][tag])
    elif(event["httpMethod"])=='POST':
        taglist=list(json.loads(event['body'])['tags'])
        
    else:
        print("only GET AND PUT allowed")
        
    scan = table.scan()
    url_list=[]
    
    for i in scan['Items']:
        if all(element in i['data'] for element in taglist):
            url_list.append(i['url'])
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({'LINKS': url_list})
    }

