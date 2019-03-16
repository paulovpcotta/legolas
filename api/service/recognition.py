import pickle
import face_recognition

ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'jpeg'}
TOLERANCE = 0.6

def predict_frame(img_frame, bounding_boxes, knn_clf=None, model_path='model-weights/trained_cnn_location_knn_model_dataset.clf', n_neighbors=1, distance_threshold=0.6):

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # Load image file and find face locations
    X_face_locations = bounding_boxes

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
