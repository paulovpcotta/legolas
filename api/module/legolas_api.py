from flask import Blueprint, request, jsonify
from service.yolo import YOLO, detect_boxes_in_image

api = Blueprint('api', __name__)
yolo = YOLO()

@api.route('/detection', methods=['POST'])
def detection():
    """
        Input: Imagem em base64
        Return: imagem em base64, lista vazia ou não 
    """

    req = request.json()
    base_64 = req['base64']

    box_list = detect_boxes_in_image(base_64, detector)

    data_dict = {'image': base_64, 'box': box_list}

    return jsonify(data_dict)


@api.route('/recognition', methods=['POST'])
def recognition():
    """
        Input: frame inteiro e posições encontrada
        Return: (label, (bounding box))
    """

    req = request.json()

    base_64 = req['base64'] 
    bounding_boxes = req['bounding_boxes']

    return jsonify()

@api.route('/detection_recognition', methods=['POST'])
def detection_and_recognition():
    """
        Input: Imagem em base64
        Return: (label, (bounding box))
    """

    req = request.json()
    base_64 = req['base64']
    
    req = request.json()
    base_64 = req['base64']

    box_list = detect_boxes_in_image(base_64, detector)

    if box_list:
        print('Recognition!')

    return jsonify()

