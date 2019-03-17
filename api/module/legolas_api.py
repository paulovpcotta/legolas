# *******************************************************************
#
# Author : Gabriel Nogueira, 2019
# C-Key  : c1297800
# Project Github : https://github.com/paulovpcotta/legolas
#
# *******************************************************************
from flask import Blueprint, request, jsonify
from service.yolo import YOLO, detect_boxes_in_image
from service.recognition import predict_frame
import base64

api = Blueprint('api', __name__)
yolo = YOLO()

@api.route('/detection', methods=['POST'])
def detection():
    """
    This function use a neural network called Yolo, this network is the state of the art 
    in the detection of objects in real time. Here we use weights from a project in github
    called yoloface, especialized in face detection.

    link to yoloface: https://github.com/davidsandberg/facenet

    Route: localhost:2931/api/detection

    Params:    
        - base64: a image encode as base 64.
    Return: 
        A dict with the image encoded as base 64 and the bouding boxes of the faces
        found in the image.
    """

    req = request.json
    base_64 = req['base64']

    image = base64.decodebytes(base_64) 

    bounding_boxes = detect_boxes_in_image(image, detector)

    data_dict = {'image': base_64, 'box': bounding_boxes}

    return jsonify(data_dict)


@api.route('/recognition', methods=['POST'])
def recognition():
    """
    The face recognition method used in here is based in a KNN model.

    Route: localhost:2931/api/detection

    Params:    
        - base64: a image encode as base 64.
        - bounding_boxes: list of bounding boxes of faces to do the recogintion.
    Return: 
        A dict with the image encoded as base 64 and a tuple containing the label and the bouding boxes
    """

    req = request.json

    base_64 = req['base64'] 
    bounding_boxes = req['bounding_boxes']

    image = base64.decodebytes(base_64) 
    data_dict = {'image':base_64, 'predict': predict_frame(image, bounding_boxes)}

    return jsonify(data_dict)

@api.route('/detection_recognition', methods=['POST'])
def detection_and_recognition():
    """
    Join of dectection and recognition, here we verify first if exist a face in the image
    using the face detection method, if found a face then we do the face recognition.

    Route: localhost:2931/api/detection_recognition  

    Input: 
        - base64: a image encode as base 64.
    Return: 
        A dict with the image encoded as base 64 and a tuple containing the label and the bouding boxes

    """
    
    req = request.json
    base_64 = req['base64']
    image = base64.decodebytes(base_64) 

    bounding_boxes = detect_boxes_in_image(image, detector)

    if bounding_boxes:
        image = base64.decodebytes(base_64) 
        data_dict = {'image':base_64, 'predict':predict_frame(image, bounding_boxes)}

    return jsonify(data_dict)

