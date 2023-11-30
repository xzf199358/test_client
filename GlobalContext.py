import json
import os
# -*- coding: UTF-8 -*-
# This module is to store all the information that dispatch algorithms need
import threading
import numpy as np
from PIL import Image
from SqlCollection import SqlCollection
import DatabaseInterface
from LoggerModule import Logger
from pyts.image import GramianAngularField
import matplotlib
from matplotlib import image

from skimage import io,transform,color
from predict_func import predict
'''
全局信息
'''
class DispatchContext:
    frequency = None
    location = None  # 1 2 3 4 5 6 7
    test_time:int = None # 1 2 3  测试次数
    db_connect = None
    path = './data2/image/'

    time:list = None
    value:list = None


    #TODO: 这里的一阶导数 为 速度  二阶导数为 角速度
    one_dif:list = None
    two_dif:list = None

    time_seg:list = None  #单组数据分割
    data_seg:list = None

    all_lock = threading.Lock()

    # # transaction image
    # img_sz = 224  # 生成的 GAF 图片的大小 (the size of each GAF image)
    # # 如果 滑动窗口的大小 等于 滑动步长 则滑动窗口之间没有重叠
    # window_sz = 3125  # 滑动窗口的大小，需要满足 window_sz > img_sz
    # step = 3125  # 滑动窗口的步长 (step of slide window)
    # method = 'summation'  # GAF 图片的类型，可选 'summation'（默认）和 'difference'

    image_list:list = None

    Counter = 0
    system_status:bool = None
    response_list = []

    predict_info = None


    beam_status:int = 1


    @classmethod
    def load_selected_data(cls):
        _,cls.value = cls.process_condition_data()
        cls.time = [i for i in range(319*3125)]
        cls.data_seg,cls.time_seg = cls.segment_data(cls.value,cls.time)
        cls.one_dif,cls.two_dif = cls.difunc(cls.data_seg,cls.time_seg)

        # cls.time_seg = [ [j for j in range(i*3125,(i+1)*3125)] for i in range(0,319)]
        # print(cls.time_seg[1:5] )
        # DispatchContext.all_lock.acquire()  #

        '''此处开始生成图像  进行数据的预测'''
        cls.image_list = cls.Transform_Image(cls.data_seg)
        # DispatchContext.all_lock.release()
        #TODO:这里执行预测函数 并将预测结果存入list中
        cls.predict_info = cls.Prediction(cls.image_list)


        return 0


    @classmethod
    def process_condition_data(cls):
        sql_sentence = SqlCollection.get_selected_data.format(
            test_name = "'" + str(cls.location)+ "-" + str(cls.test_time) + "'"
        )
        print("sql_sentence",sql_sentence)
        try:
            rows,_ = send_data_to_database('get selected data', sql_sentence)
        except Exception as e:
            Logger.error('error  value ' + str(e))
        time,value = [],[]
        for row in rows:

            time.append(row[0])
            value.append(row[1])
        cls.time = time
        cls.value = value

        return time,value
    @classmethod
    def segment_data(cls,data: list, time_list: list) -> list:
        '''
        按照所需的数据长度进行分割 返回为 list  按照一个完整地波形进行分割
        :return:
        '''
        _, start = cls.find_max(data[0:2000])
        seg_data = []
        seg_time = []
        for i in range(319):
            seg_data.append(data[start + i * 3125:3125 * (i + 1) + start])
            seg_time.append(time_list[i * 3125:3125 * (i + 1) ])
        return seg_data, seg_time

    #开始对元数据进行 求导数操作
    @classmethod
    def difunc(cls,data_y: list, time_list: list) -> list:
        y_one = []
        y_two = []
        Logger.info("Beigin to diff one data!!")
        for i in range(len(data_y)):
            '''求一阶导数'''
            y_one.append(list(np.gradient(data_y[i], time_list[i][1]-time_list[i][0])))

        Logger.info("Begin to diff two data!!!!")
        for j in range(len(y_one)):
            y_two.append(list(np.gradient(y_one[j], time_list[j][1] - time_list[j][0])))

        # print("Diff one  {}".format(y_one))

        return y_one ,y_two




    @classmethod
    def find_max(cls,value):
        '''
        查找一段数据区间内最大值
        :param value:
        :return:
        '''
        max_value = 0
        index = 0
        for i in range(len(value)):
            if value[i] > max_value:
                max_value = value[i]
                index = i
            else:
                continue
        return max_value, index

    @classmethod
    def Transform_Image(cls,data_list: list) -> list:
        # 生成整组数据的 角度场图像
        # transaction image
        path = './data/image/'
        img_sz = 28  # 生成的 GAF 图片的大小 (the size of each GAF image)
        # 如果 滑动窗口的大小 等于 滑动步长 则滑动窗口之间没有重叠
        window_sz = 3125  # 滑动窗口的大小，需要满足 window_sz > img_sz
        step = 3125  # 滑动窗口的步长 (step of slide window)
        method = 'summation'  # GAF 图片的类型，可选 'summation'（默认）和 'difference'
        img_path = path + '/'
        if not os.path.exists(img_path):
            os.makedirs(img_path)  # 如果文件夹不存在就创建一个
        Gen_image = []
        # data_list,time_list = segment_data(data)  # 这里对每一组数据 都会进行分割 40
        # DispatchContext.time = time_list
        # DispatchContext.value = data_list



        for i in range(len(data_list)):
            data_pro = np.array(data_list[i]).reshape(1, -1)
            _, n_sample = data_pro.shape
            Logger.info("开始生成图像...")
            gaf = GramianAngularField(image_size=img_sz, method=method)
            img_num = 0  # 生成图片的总数 (the total numbers of GAF images)
            start_index, end_index = 0, window_sz  # 序列开头以及末尾索引
            while end_index <= n_sample:
                img_num += 1
                sub_series = data_pro[:, start_index:end_index]
                gaf_img = gaf.fit_transform(sub_series)  # 转化为 GAF 图片
                img_save_path = img_path + "{}.jpg".format(i)
                imag = gaf_img[0]
                print(type(image),"type")
                # gray = color.rgb2gray(image)
                image.imsave(img_save_path, gaf_img[0])  # 保存图片 (save image)
                img = transform.resize(imag, (img_sz, img_sz))
                Gen_image.append(img)
                start_index += step
                end_index += step
        Logger.info("图像生成结束！！！！")
        print(Gen_image[0].shape)
        return_img = np.asarray(Gen_image,np.float32)
        print(return_img.shape)
        return return_img

    @classmethod
    def Prediction(cls,image_list: list):
        # result_class = []
        im_height = 28
        im_width = 28
        num_classes = 7
        '''
         用于 读取转换成的图像数据 进行结果的预测
        :return:
        '''
        print('image_list',type((image_list[0])))
        result_class_list = predict(image_list)

        return result_class_list





def send_data_to_database(table,sql_sentence)->int:
    Logger.info('write the data  into database table={}'.format(table))
    rows, error_info = DatabaseInterface.execute_commit_sql(DispatchContext.db_connect, sql_sentence)
    if error_info is not None or rows is None:
        Logger.error('send_io_data_to_database error!!! error_info: ' + str(error_info))
        return 404
    return rows,error_info




def set_data_to_None():
    '''
    进行数据的初始化
    :return:
    '''
    #进行初始化
    DispatchContext.all_lock.acquire()
    try:
        DispatchContext.frequency = None
        DispatchContext.location = None  # 1 2 3 4 5 6 7
        DispatchContext.test_time = None  # 1 2 3  测试次数
        DispatchContext.time = None
        DispatchContext.value = None
        DispatchContext.time_seg = None  # 单组数据分割
        DispatchContext.data_seg = None
        DispatchContext.one_dif= None
        DispatchContext.two_dif= None
        DispatchContext.image_list = None
        DispatchContext.Counter = 0
        DispatchContext.system_status = None
        DispatchContext.response_list = []
        DispatchContext.predict_info = None
        DispatchContext.beam_status = 1
    except Exception as e:
        Logger.error(repr(e))
    DispatchContext.all_lock.release()



if __name__ == "__main__":
    with open("./123.txt", "r") as f:  # 打开文件
        data = f.read()  # 读取文件
        print(type(data))
