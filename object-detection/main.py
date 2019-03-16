import argparse
import base64

from yolo.yolo import YOLO, detect_boxes_in_image

#####################################################################
def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--model', type=str, default='model-weights/YOLO_Face.h5',
                        help='path to model weights file')
    parser.add_argument('--anchors', type=str, default='cfg/yolo_anchors.txt',
                        help='path to anchor definitions')
    parser.add_argument('--classes', type=str, default='cfg/face_classes.txt',
                        help='path to class definitions')
    parser.add_argument('--score', type=float, default=0.5,
                        help='the score threshold')
    parser.add_argument('--iou', type=float, default=0.45,
                        help='the iou threshold')
    parser.add_argument('--img-size', type=list, action='store',
                        default=(416, 416), help='input image size')
    parser.add_argument('--image', default=False, action="store_true",
                        help='image detection mode')
    parser.add_argument('--video', type=str, default='samples/subway.mp4',
                        help='path to the video')
    parser.add_argument('--output', type=str, default='outputs/',
                        help='image/video output path')

    args = parser.parse_args()

    return args

#####################################################################
def detect_face_in_image(image_as_base64):
    args = get_args()
    detector = YOLO(args)

    box_list = detect_boxes_in_image(image_as_base64, detector)

    data_dict = {'image': image_as_base64, 'box': box_list}

    return data_dict

#####################################################################
def _main():
    im = input('Filename: ')

    try:
        with open(im, "rb") as image:
            base64_image = base64.b64encode(image.read())

            response = detect_face_in_image(base64_image)
            
            print(response) 

    except:
        print('erro')

#####################################################################
if __name__ == "__main__":
    _main()
