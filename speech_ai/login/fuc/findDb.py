import warnings

warnings.filterwarnings("ignore")

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import time
from os import path
from tqdm import tqdm
import pickle

from deepface.basemodels import VGGFace, OpenFace, Facenet, Facenet512, FbDeepFace, DeepID, DlibWrapper, ArcFace, \
    Boosting, SFaceWrapper
from deepface.extendedmodels import Age, Gender, Race, Emotion
from deepface.commons import functions

import tensorflow as tf

tf_version = int(tf.__version__.split(".")[0])
if tf_version == 2:
    import logging

    tf.get_logger().setLevel(logging.ERROR)


def build_model(model_name):
    global model_obj  # singleton design pattern

    models = {
        'VGG-Face': VGGFace.loadModel,
        'OpenFace': OpenFace.loadModel,
        'Facenet': Facenet.loadModel,
        'Facenet512': Facenet512.loadModel,
        'DeepFace': FbDeepFace.loadModel,
        'DeepID': DeepID.loadModel,
        'Dlib': DlibWrapper.loadModel,
        'ArcFace': ArcFace.loadModel,
        'SFace': SFaceWrapper.load_model,
        'Emotion': Emotion.loadModel,
        'Age': Age.loadModel,
        'Gender': Gender.loadModel,
        'Race': Race.loadModel
    }

    if not "model_obj" in globals():
        model_obj = {}

    if not model_name in model_obj.keys():
        model = models.get(model_name)
        if model:
            model = model()
            model_obj[model_name] = model
        # print(model_name," built")
        else:
            raise ValueError('Invalid model_name passed - {}'.format(model_name))

    return model_obj[model_name]


def findDb(db_path, model_name='VGG-Face', distance_metric='cosine', model=None, enforce_detection=True,
           detector_backend='opencv', align=True, prog_bar=True, normalization='base', silent=False):
    if os.path.isdir(db_path) == True:

        if model == None:

            if model_name == 'Ensemble':
                if not silent: print("Ensemble learning enabled")
                models = Boosting.loadModel()

            else:  # model is not ensemble
                model = build_model(model_name)
                models = {}
                models[model_name] = model

        else:  # model != None
            if not silent: print("Already built model is passed")

            if model_name == 'Ensemble':
                Boosting.validate_model(model)
                models = model.copy()
            else:
                models = {}
                models[model_name] = model

        # ---------------------------------------

        if model_name == 'Ensemble':
            model_names = ['VGG-Face', 'Facenet', 'OpenFace', 'DeepFace']
            metric_names = ['cosine', 'euclidean', 'euclidean_l2']
        elif model_name != 'Ensemble':
            model_names = [];
            metric_names = []
            model_names.append(model_name)
            metric_names.append(distance_metric)

        # ---------------------------------------

        file_name = "representations_%s.pkl" % (model_name)
        file_name = file_name.replace("-", "_").lower()

        if path.exists(db_path + "/" + file_name):

            if not silent: print("WARNING: Representations for images in ", db_path,
                                 " folder were previously stored in ", file_name,
                                 ". If you added new instances after this file creation, then please delete this file and call find function again. It will create it again.")

            f = open(db_path + '/' + file_name, 'rb')
            representations = pickle.load(f)

            if not silent: print("There are ", len(representations), " representations found in ", file_name)

        else:  # create representation.pkl from scratch
            employees = []

            for r, d, f in os.walk(db_path):  # r=root, d=directories, f = files
                for file in f:
                    if ('.jpg' in file.lower()) or ('.png' in file.lower()):
                        exact_path = r + "/" + file
                        employees.append(exact_path)

            if len(employees) == 0:
                raise ValueError("There is no image in ", db_path,
                                 " folder! Validate .jpg or .png files exist in this path.")

            # ------------------------
            # find representations for db images

            representations = []

            pbar = tqdm(range(0, len(employees)), desc='Finding representations', disable=prog_bar)

            # for employee in employees:
            for index in pbar:
                employee = employees[index]

                instance = []
                instance.append(employee)

                for j in model_names:
                    custom_model = models[j]

                    representation = represent(img_path=employee
                                               , model_name=model_name, model=custom_model
                                               , enforce_detection=enforce_detection, detector_backend=detector_backend
                                               , align=align
                                               , normalization=normalization
                                               )

                    instance.append(representation)

                # -------------------------------

                representations.append(instance)

            f = open(db_path + '/' + file_name, "wb")
            pickle.dump(representations, f)
            f.close()

        # if not silent: print("Representations stored in ",db_path,"/",file_name," file. Please delete this file when you add new identities in your database.")


def represent(img_path, model_name='VGG-Face', model=None, enforce_detection=True, detector_backend='opencv',
              align=True, normalization='base'):
    if model is None:
        model = build_model(model_name)

    # ---------------------------------

    # decide input shape
    input_shape_x, input_shape_y = functions.find_input_shape(model)

    # detect and align
    img = functions.preprocess_face(img=img_path
                                    , target_size=(input_shape_y, input_shape_x)
                                    , enforce_detection=enforce_detection
                                    , detector_backend=detector_backend
                                    , align=align)

    # ---------------------------------
    # custom normalization

    img = functions.normalize_input(img=img, normalization=normalization)

    # ---------------------------------

    # represent
    embedding = model.predict(img)[0].tolist()

    return embedding
