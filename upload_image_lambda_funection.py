import json
import cv2
import boto3
import numpy as np
from urllib.parse import unquote_plus

s3=boto3.client('s3')
dynamodb=boto3.client('dynamodb')
table='Url-Tags'



config_threshold=0.5
nms_threshold=0.1



def lambda_handler(event,context):
    
    #downloading the yolo configiration file from s3
    yolo_bucket='objectdetection-yolo-files'
    yolo_configiration='yolov3.cfg'
    cfg_file='/tmp/yolov3.cfg'
    s3.download_file(yolo_bucket, yolo_configiration, cfg_file)  
   
    
    #downloading the yolo weights file from s3
    yolo_weights_file='yolov3.weights'
    weights_file='/tmp/yolov3.weights'
    s3.download_file(yolo_bucket, yolo_weights_file, weights_file)  

    
    
    
    #downloading the labels file from s3(training set)
    yolo_labels_file='coco.names'
    labels_file='/tmp/coco.names'
    s3.download_file(yolo_bucket, yolo_labels_file, labels_file)  
   
    
    
    #getting the uploaded image from s3, for which the object detection will be done #1 get bucket name #2 - Get the file/key name
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    print(bucket_name)
    name = unquote_plus(event['Records'][0]['s3']['object']['key'])
    file_name =  name
    print(file_name)
    print("File {0} uploaded to {1} bucket".format(file_name, bucket_name))
    uploadedImage = s3.get_object(Bucket=bucket_name, Key=file_name)
    print("uploaded iamge")
    
    
    
    #getting the uploaded image from s3, for which the object detection will be done
    Bucket = 'imguploads3-bucket'
    Key =  file_name
    File = '/tmp/uploaded_image.jpg'
    s3.download_file(Bucket, Key, File)  
    
    
    data = {}
    image_tags=get_predection('/tmp/uploaded_image.jpg')
    print("image_tags",image_tags)
    tag=','.join(image_tags)
    data['url'] = {'S': 'https://imguploads3-bucket.s3.amazonaws.com/'+ Key}
    data['data'] = {'S': tag }
    
    # Strong the json object in the dynamo DB
    response = dynamodb.put_item(TableName=table, Item=data)
    print(response)
    
    
    return{
        'statusCode': '200' ,
        'body' : 'response'
    }
    
    

    
def get_predection(image):
    image=cv2.imread(image)
    (H, W) = image.shape[:2]
    net = cv2.dnn.readNetFromDarknet('/tmp/yolov3.cfg','/tmp/yolov3.weights')
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)
    boxes = []
    confidences = []
    classIDs = []
    global objects
    objects = []
    label = open('/tmp/coco.names').read().strip().split("\n")


    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            
            if confidence > config_threshold:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)
                
    idxs = cv2.dnn.NMSBoxes(boxes, confidences,config_threshold,nms_threshold)
    np.random.seed(42)
    colors = np.random.randint(0, 255, size=(len(label), 3), dtype="uint8")
    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            color = [int(c) for c in colors[classIDs[i]]]
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            labels = "{}".format(label[classIDs[i]])
            objects.append(labels)
    return objects            
    
    
                
                
                
    
                
               
                        
                        

    
    
    




