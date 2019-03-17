# *******************************************************************
#
# Author : Thanh Nguyen, 2018
# Email  : sthanhng@gmail.com
# Github : https://github.com/sthanhng
#
# Face detection using the YOLOv3 algorithm
#
# Description : yolo.py
# Contains methods of YOLO
#
# *******************************************************************

import io
import os
import colorsys
import numpy as np
import cv2
import base64

from service.model import eval

from keras import backend as K
from keras.models import load_model
from timeit import default_timer as timer
from PIL import ImageDraw, Image

import skimage.io

import logging

####################################################################

class YOLO(object):
    def __init__(self):
        self.model_path = 'model-weights/YOLO_Face.h5' 
        self.classes_path = 'cfg/face_classes.txt'
        self.anchors_path = 'cfg/yolo_anchors.txt'
        self.class_names = self._get_class()
        self.anchors = self._get_anchors()
        self.sess = K.get_session()
        self.boxes, self.scores, self.classes = self._generate()
        self.model_image_size = (416, 416)

#####################################################################
    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

#####################################################################
    def _get_anchors(self):
        anchors_path = os.path.expanduser(self.anchors_path)
        with open(anchors_path) as f:
            anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        return np.array(anchors).reshape(-1, 2)

#####################################################################
    def _generate(self):
        logger = logging.getLogger(__name__)

        model_path = os.path.expanduser(self.model_path)
        
        assert model_path.endswith('.h5'), 'O modelo do Keras deve ser um arquivo do tipo .h5'

        num_anchors = len(self.anchors)
        num_classes = len(self.class_names)
        
        try:
            self.yolo_model = load_model(model_path, compile=False)
        except:
            self.yolo_model.load_weights(self.model_path)
        else:
            assert self.yolo_model.layers[-1].output_shape[-1] == \
                   num_anchors / len(self.yolo_model.output) * (
                           num_classes + 5), \
                'Mismatch entre modelo e imagens'
        
        logger.info('_generate: Modelo {}, âncores de classes foram carregados com sucesso'.format(model_path))

        hsv_tuples = [(x / len(self.class_names), 1., 1.)
                      for x in range(len(self.class_names))]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(
            map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                self.colors))

        # shuffle colors to decorrelate adjacent classes.
        np.random.seed(102)
        np.random.shuffle(self.colors)
        np.random.seed(None)

        logger.info('_generate: Executando o modelo para busca de bounding boxes na imagem')

        self.input_image_shape = K.placeholder(shape=(2,))
        
        boxes, scores, classes = eval(self.yolo_model.output, self.anchors,
                                           len(self.class_names),
                                           self.input_image_shape,
                                           score_threshold=0.5,
                                           iou_threshold=0.45)
        return boxes, scores, classes

#####################################################################
    def detect_boxes(self, image):
        logger = logging.getLogger(__name__)

        start_time = timer()

        try:
            logger.info('detect_boxes: Re-dimensionando a imagem')

            if self.model_image_size != (None, None):
                assert self.model_image_size[0] % 32 == 0, 'É necessário que a imagem seja múltipla de 32'
                assert self.model_image_size[1] % 32 == 0, 'É necessário que a imagem seja múltipla de 32'

                boxed_image = letterbox_image(image, tuple(reversed(self.model_image_size)))
            else:
                new_image_size = (image.width - (image.width % 32),
                                  image.height - (image.height % 32))

                boxed_image = letterbox_image(image, new_image_size)

            image_data = np.array(boxed_image, dtype='float32')

            logger.info('detect_boxes: Tamanho da imagem: '+ str(image_data.shape))

            image_data /= 255.

            image_data = np.expand_dims(image_data, 0)

            logger.info('detect_boxes: Buscando faces na imagem...')

            out_boxes, out_scores, out_classes = self.sess.run(
                [self.boxes, self.scores, self.classes],
                feed_dict={
                    self.yolo_model.input: image_data,
                    self.input_image_shape: [image.size[1], image.size[0]]#, K.learning_phase(): 0
                })

            logger.info('detect_boxes: Foram encontradas {} face(s) nesta imagem'.format(len(out_boxes)))
            logger.info('detect_boxes: Obtendo a lista de boxes')

            boxes = list()

            for box in out_boxes:
                top, left, bottom, right = box

                top = max(0, np.floor(top + 0.5).astype('int32'))
                left = max(0, np.floor(left + 0.5).astype('int32'))
                bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
                right = min(image.size[0], np.floor(right + 0.5).astype('int32'))

                boxes.append((int(top), int(right), int(bottom), int(left)))

            end_time = timer()
            
            logger.info('detect_boxes: Processamento concluído em {:.2f}ms'.format((end_time - start_time) * 1000))
            
            return boxes
        except:
            logger.error('detect_boxes: Erro ao processar a imagem', exc_info=True)

            return []

####################################################################
    def close_session(self):
        logger = logging.getLogger(__name__)

        logger.info('close_session: Fechando a sessão do Tensorflow')
        
        self.sess.close()

####################################################################
def letterbox_image(image, size):
    logger = logging.getLogger(__name__)

    logger.info('letterbox_image: Redimensionando a imagem sem perder o aspecto da mesma')

    img_width, img_height = image.size
    w, h = size
    scale = min(w / img_width, h / img_height)
    nw = int(img_width * scale)
    nh = int(img_height * scale)

    image = image.resize((nw, nh), Image.BICUBIC)

    new_image = Image.new('RGB', size, (128, 128, 128))
    new_image.paste(image, ((w - nw) // 2, (h - nh) // 2))

    return new_image

####################################################################
def detect_boxes_in_image(image_as_base64, detector):
    logger = logging.getLogger(__name__)
    boxes = []

    try:
        logger.info('detect_boxes_in_image: Decodificando o array contendo a imagem')

        if isinstance(image_as_base64, bytes):
            image_as_base64 = image_as_base64.decode("utf-8")

        image_data = base64.b64decode(image_as_base64)

        logger.info('detect_boxes_in_image: Obtendo a imagem em formato PIL')

        image = Image.open(io.BytesIO(image_data))
    except:
        logger.info('detect_boxes_in_image: Erro ao obter a imagem', exc_info=True)

        return []
    else:
        logger.info('detect_boxes_in_image: Realizando a detecção')

        boxes = detector.detect_boxes(image)

    return boxes


