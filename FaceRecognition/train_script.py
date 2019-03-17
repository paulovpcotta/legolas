from multiprocessing import Queue, Process
import math
from sklearn import neighbors
from tqdm import tqdm
import os
import os.path
import pickle
from PIL import Image, ImageDraw
import cv2
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
from time import time

ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'jpeg'}
TOLERANCE = 0.6

def train(train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):

    X = []
    y = []

    # Loop through each person in the training set
    for class_dir in os.listdir(train_dir):

        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue

        # Loop through each training image for the current person
        list_images_path = [os.path.join(train_dir, class_dir, x) \
                for x in os.listdir(os.path.join(train_dir, class_dir)) \
                    if os.path.isfile(os.path.join(train_dir, class_dir, x))]

        for img_path in list_images_path: #image_files_in_folder(os.path.join(train_dir, sub_dataset, class_dir)):
            print(img_path)

            # image = face_recognition.load_image_file(img_path)

            if len(img_path.split('.')) == 3:
                image = face_recognition.load_image_file(img_path)

            elif img_path.split('.')[3] in ALLOWED_EXTENSIONS:
                image = face_recognition.load_image_file(img_path)
    
            else:
                continue

            H, W = image.shape[0], image.shape[1]

            if H > 1000 or W > 1000:

                if W > H:
                    r = 624.0 / W
                    dim = (624, int(H*r)-1)
                else:
                    r = 624.0 / H
                    dim = (int(W*r)-1, 624)
                
                image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

            start = time()
            face_bounding_boxes = face_recognition.face_locations(image, model='cnn') # model="cnn"
            print(face_bounding_boxes)
            delta_t = time() - start

            print('cnn time --> ', delta_t)

            if len(face_bounding_boxes) != 1:
                # If there are no people (or too many people) in a training image, skip the image.
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                # Add face encoding for current image to the training set
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes, num_jitters = 2)[0]) # num_jitter = 2 
                y.append(class_dir)


    # Determine how many neighbors to use for weighting in the KNN classifier
    print('num samples --> ', len(X))
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf


def predict_frame(img_frame, knn_clf=None, model_path=None, n_neighbors=1, distance_threshold=0.6):

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # Load image file and find face locations
    X_face_locations = face_recognition.face_locations(img_frame)#, model='cnn')

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return []

    # Find encodings for faces in the test image
    faces_encodings = face_recognition.face_encodings(img_frame, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=n_neighbors)

    are_matches = []

    for i in range(len(X_face_locations)):
        list_k_distances = [closest_distances[0][i][j] for j in range(n_neighbors)]

        if min(list_k_distances) <= distance_threshold:
            are_matches.append(True)
        else:
            are_matches.append(False)
    
    # Get predictions, locations and if it was recognized
    predictions = []

    for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches):

        if rec:
            predictions.append((pred,loc))
        else:
            predictions.append(("unknown",loc))

    # Predict classes and remove classifications that aren't within the threshold
    return predictions


def plot_frames(q_plot):
    window_name = "FACE BB"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    while True:
        frame = q_plot.get()
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)


def draw_rectangle(image, predictions):
    for name, (top, right, bottom, left) in predictions:
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 3)
        W = (right - left)//2 #+W-(W//2)
        cv2.putText(image, name, (left, top - 7), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0))
    return image


def match_images_frame(q_plot, camera = None, model_path="weights/trained_cnn_location_knn_model_dataset.clf", n_neighbors=1):

    # Load a trained KNN model (if one was passed in)
    with open(model_path, 'rb') as f:
        knn_clf = pickle.load(f)

    frame_rate, frame_count = 6, 0

    if camera:
        cap = cv2.VideoCapture(camera)
    else:
        cap = cv2.VideoCapture(0) # 30FPS my laptop
  
    while True:

        ret, frame = cap.read()

        if not ret:
            break
        
        #predictions = []

        if (frame_count % frame_rate) == 0:
        
            predictions = predict_frame(frame, model_path=model_path, distance_threshold=TOLERANCE, n_neighbors=n_neighbors)

            #if predictions:
            #frame_to_print = frame if not frame.any() else frame
            q_plot.put(draw_rectangle(frame, predictions))


        frame_count += 1

    cap.release()






if __name__ == "__main__":
    # STEP 1: Train the KNN classifier and save it to disk
    # Once the model is trained and saved, you can skip this step next time.
    print("Training KNN classifier...")
    classifier = train("../training_dataset", model_save_path="weights/trained_cnn_location_knn_model_dataset.clf", verbose=True, n_neighbors=11)
    print("Training complete!")

    # # STEP 2: Using the trained classifier, make predictions for unknown images from camera
    # q_plot = Queue()
    # p2 = Process(target=plot_frames, args=(q_plot,))
    # p2.start()

    # match_images_frame(q_plot, model_path="weights/trained_cnn_location_knn_model_dataset.clf", n_neighbors=9)
