import numpy as np
from keras.preprocessing import image
from keras.applications.mobilenet import MobileNet, preprocess_input, decode_predictions

class imagenet():
    def __init__(self,model):
        self.model = model
    def predict(self, img):
        img = image.load_img(img, target_size=(128, 128))
        img = image.img_to_array(img).reshape(1,128,128,3)
        pred = self.model.predict(preprocess_input(img))
        top = decode_predictions(pred, top=5)
        desc = []
        score = []
        for i in range(5):
            desc.append(top[0][i][1])
            score.append(top[0][i][2]*100)
        return desc, score
