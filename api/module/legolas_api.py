# *******************************************************************
#
# Author : Gabriel Nogueira & Hialo Muniz, 2019
# C-Key  : c1297800, c1298437
# Project Github : https://github.com/paulovpcotta/legolas
#
# *******************************************************************
from flask import Blueprint, request, jsonify
from service.yolo import YOLO, detect_boxes_in_image
from service.recognition import predict_frame
from service.utils import decode_image_from_base64

import base64
import pickle

import logging

from PIL import ImageDraw, Image
import io

api = Blueprint('api', __name__)
detector = YOLO()

####################################################################
@api.route('/detection', methods=['POST'])
def detection():
    """
    This function use a neural network called Yolo, this network is the state of the art 
    in the detection of objects in real time. Here we use weights from a project in github
    called yoloface, especialized in face detection.

    link to yoloface: https://github.com/davidsandberg/facenet

    Uri: localhost:2931/api/detection

    Params:    
        - base64: a image encode as base 64.
    Return: 
        A dict with the image encoded as base 64 and the bouding boxes of the faces
        found in the image.
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("detection: Obtendo dados da requisição")

        request_data = request.get_json()

        image_as_base64 = request_data['base64']
    except:
        logger.error('detection: O conteúdo da requisição está vazio ou é inválido')

        return jsonify({'image': None, 'bounding_boxes': None}, 400)

    try:
        logger.info("detection: Verificando se existem faces na imagem")

        bounding_boxes = detect_boxes_in_image(image_as_base64, detector)

        data_dict = {'image': image_as_base64, 'bounding_boxes': bounding_boxes}

        return jsonify(data_dict)
        
    except Exception as err:

        logger.error('detection: Erro ao executar a operação: %s', str(err), exc_info=True)

        return jsonify({'image': None, 'bounding_boxes': None})

####################################################################
@api.route('/recognition', methods=['POST'])
def recognition():
    """
    The face recognition method used in here is based in a KNN model.

    Uri: localhost:2931/api/detection

    Params:    
        - base64: a image encode as base 64.
        - bounding_boxes: list of bounding boxes of faces to do the recogintion.
    Return: 
        A dict with the image encoded as base 64 and a tuple containing the label and the bouding boxes
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("recognition: Obtendo dados da requisição")

        request_data = request.get_json()

        image_as_base64 = request_data['base64']
        bounding_boxes = request_data['bounding_boxes']
    except:
        logger.error('recognition: O conteúdo da requisição está vazio ou é inválido')

        return jsonify({'image': None, 'box': None}, 400)

    try:
        if bounding_boxes:
            logger.info("recognition: Buscando faces na imagem")

            image = decode_image_from_base64(image_as_base64)

            data_dict = {'image': image_as_base64, 'predict': predict_frame(image, bounding_boxes, n_neighbors=11)}

            return jsonify(data_dict)
        else:
            return jsonify({'image': image_as_base64, 'predict': None})
    except Exception as err:
        logger.error('recognition: Erro ao executar a operação: %s', str(err), exc_info=True)

        return jsonify({'image': None, 'predict': None})

####################################################################
@api.route('/detection_recognition', methods=['POST'])
def detection_and_recognition():
    """
    Join of dectection and recognition, here we verify first if exist a face in the image
    using the face detection method, if found a face then we do the face recognition.

    Uri: localhost:2931/api/detection_recognition  

    Input: 
        - base64: a image encode as base 64.
    Return: 
        A dict with the image encoded as base 64 and a tuple containing the label and the bouding boxes

    """

    logger = logging.getLogger(__name__)

    try:
        logger.info("detection_and_recognition: Obtendo dados da requisição")

        request_data = request.get_json()

        image_as_base64 = request_data['base64']
    except:
        logger.error('detection_and_recognition: O conteúdo da requisição está vazio ou é inválido')

        return jsonify({'image': None, 'box': None}, 400)

    try:
        logger.info("detection_and_recognition: Verificando se existem faces na imagem")

        bounding_boxes = detect_boxes_in_image(image_as_base64, detector)

        if bounding_boxes:
            logger.info("detection_and_recognition: {} bounding boxes encontrados.".format(len(bounding_boxes)))
            logger.info("detection_and_recognition: Buscando faces na imagem")

            image = decode_image_from_base64(image_as_base64)

            predictions = predict_frame(image, bounding_boxes, n_neighbors=11)

            pred_list = []
            for prediction in predictions:
                pred_list.append({'name': prediction[0], 'box': prediction[1]})

            data_dict = {'image': image_as_base64, 'predict': pred_list}

            return jsonify(data_dict)
        else:
            return jsonify({'image': image_as_base64, 'predict': None})
    except Exception as err:
        logger.error('detection_and_recognition: Erro ao executar a operação: %s', str(err), exc_info=True)

        return jsonify({'image': None, 'predict': None})
    
