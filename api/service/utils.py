import numpy as np
import skimage.io
import logging
import base64

####################################################################
def decode_image_from_base64(image_as_base64):
    """
    Realiza a decodificação da imagem em formato base64,
    e salva a imagem em uma pasta temporária para ser lida.

    :param image_as_base64: imagem codificada em base64, no formato string
    :type image_as_base64: str

    :return: array do NumPy contendo a representação da imagem
    :rtype: ndarray
    """
    logger = logging.getLogger(__name__)

    logger.info("decode_image_from_base64: Decodificando a imagem em formato base64")

    if isinstance(image_as_base64, bytes):
        image_as_base64 = image_as_base64.decode("utf-8")

    image_data = base64.b64decode(image_as_base64)
    image = skimage.io.imread(image_data, plugin='imageio')

    return np.array(image)
