# -*- encoding: utf-8 -*-
'''
@File: predict_func.py
@Author: Zifeng Xu
@Date: 2022/12/17 22:39
@license: Copyright(C),shanghai university
@contact: xuzifeng@shu.edu.cn
@software: pycharm
'''

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

def predict(x_val):
    print("x_val", x_val)
    model = tf.keras.models.load_model("./model/model.h5")
    predictions = model.predict(x_val)
    print("predictions", predictions[0])
    pre_lable = predictions.argmax(axis=-1)
    print("pre_lable", pre_lable)
    result = list(map(lambda x:int(x+1),pre_lable))
    print("result", result)
    return result




if __name__ == "__main__":
    pass


