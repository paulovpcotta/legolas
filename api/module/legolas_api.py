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
        Input: Imagem em base64
        Return: imagem em base64, lista vazia ou não 
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
        Input: frame inteiro e posições encontrada
        Return: (label, (bounding box))
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

            data_dict = {'image': image_as_base64, 'predict': predict_frame(image, bounding_boxes)}

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
        Input: Imagem em base64
        Return: (label, (bounding box))
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

            predictions = predict_frame(image, bounding_boxes)

            print(predictions)

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
    
