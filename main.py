import os
import threading
import time

import psycopg2
import requests
from flask import Flask, jsonify,request,Blueprint
# from api import Timer
from flask_cors import *
from threading import Thread
import json
import os, sys
curpath = os.path.abspath(os.path.dirname(__file__))
rootpath = os.path.split(curpath)[0]
sys.path.append(rootpath)
from matplotlib import image
import ToolFunctions
from  GlobalContext import DispatchContext,set_data_to_None

import LoggerModule
from SqlCollection import SqlCollection
from version import program_version_no
import ConfigManager




app = Flask(__name__)
# 通过CORS，所有的来源都允许跨域访问
CORS(app, resources=r'/*')

Logger = LoggerModule.Logger

configs = ConfigManager.ConfigParameter.load_config()
LoggerModule.LoggerManager.create_logger()
Logger = LoggerModule.Logger
# db_pool = DatabaseConnectionPool.db_pool = DatabaseConnectionPool.DatabaseConnectionPool.create_pool()
db_connect = psycopg2.connect(database=configs.database_name, user=configs.database_user_name,
                              password=configs.database_password, host=configs.database_host,
                              port=configs.database_port)
DispatchContext.db_connect = db_connect

# DispatchContext.db_connect = db_pool.get_connection()
Logger.info('Current Program Version' + program_version_no)

'''
    初始化  数据库接口程序
    '''
# read sql interface files
Logger.info('start to initialize sql interfaces from reading files...')
read_result = SqlCollection.load_sql_interfaces()
if read_result < 0:
    Logger.fatal('initialize_sql_interfaces encountered an exception!')
    ToolFunctions.sys_exit(105)
Logger.info('sql interfaces were initialized.')


# try:
#     Logger.info(" starting  write image")
#     thread_dispatch_logic = threading.Thread(target = write_image_path,
#                                              name='write image')
#     thread_dispatch_logic.setDaemon(True)
#     thread_dispatch_logic.start()
# except Exception as e:
#     Logger.error("when start a new thread for write image")
#     Logger.fatal(repr(e))
#     ToolFunctions.sys_exit(106)

# def write_image_path():
#     img_path = DispatchContext.path + '/'
#     if not os.path.exists(img_path):
#         os.makedirs(img_path)  # 如果文件夹不存在就创建一个
#     img_save_path = img_path + "{}.jpg".format(1)
#     while True:
#         if DispatchContext.system_status == True and DispatchContext.image_list is not None:
#             # 开始 往指定的文件夹写入图片
#             Logger.info("start to Writing image path")
#             for img in DispatchContext.image_list:
#                 image.imsave(img_save_path, img)  # 保存图片 (save image)
#                 time.sleep(1)

def write_image_path():
    img_path = DispatchContext.path + '/'
    if not os.path.exists(img_path):
        os.makedirs(img_path)  # 如果文件夹不存在就创建一个
    img_save_path = img_path + "{}.jpg".format(1)
    # 开始 往指定的文件夹写入图片
    Logger.info("start to Writing image path")
    if DispatchContext.Counter <=319:
        image.imsave(img_save_path, DispatchContext.image_list[DispatchContext.Counter])  # 保存图片 (save image)



#unity 触发的 传递型号的要求
@app.route("/input/struct/",methods=["POST"])
def Get_input_struct():
    '''
    数据库获取对应的数据并返回  执行测试
    :return:
    interface:
    {"frequency":"8",
    "location":"7",
    "test_time":"2"
    }
    '''
    #数据进行初始化   新的一次请求开始 需要对其全部进行初始化
    set_data_to_None()
    #处理  健康预测模块回传的  型号 和时间参数
    frequency = request.json.get("frequency")
    location = request.json.get("location")
    test_time = request.json.get("test_time")

    DispatchContext.frequency = frequency
    DispatchContext.location = location
    DispatchContext.test_time = test_time
    
    # DispatchContext.load_selected_data()  #load data from database
    print('accept the request parameters {},{},{}'.format(frequency,location,test_time))
    #允许前端开始数据请求
    DispatchContext.system_status = True   #

    return_data = json.dumps({"res":888}).encode("utf-8")


    return return_data


@app.route("/status/")
def state():  #返回原始信号数据的幅值以及震动频率
    """向前端返回json类型的数据  根据接收的型号 返回查询到数据"""
    data = {
        "status": DispatchContext.system_status
    }
    return jsonify(data)




@app.route("/index/")
def index():  #返回原始信号数据
    """向前端返回json类型的数据  根据接收的型号 返回查询到数据"""
    try:
        if  DispatchContext.data_seg[DispatchContext.Counter] != None and DispatchContext.Counter <= 319:
            # write_image_path()
            # data1 = {
            #     "time": DispatchContext.time_seg[DispatchContext.Counter],
            #     "value": DispatchContext.data_seg[DispatchContext.Counter]
            # }
            data1 = {
                "time": DispatchContext.time_seg[DispatchContext.Counter],
                "value": DispatchContext.data_seg[DispatchContext.Counter],
                "y_one": DispatchContext.one_dif[DispatchContext.Counter],
                "y_two": DispatchContext.two_dif[DispatchContext.Counter]

            }
            DispatchContext.Counter += 1
        else:
            DispatchContext.system_status = False  #
            DispatchContext.frequency = None
            DispatchContext.location = None
            DispatchContext.test_time = None
            DispatchContext.predict_info = None
            DispatchContext.image_list = None
            DispatchContext.Counter = 0
            DispatchContext.time1 = None
            DispatchContext.value1 = None
            DispatchContext.time_seg = None  # 单组数据分割
            DispatchContext.data_seg = None
            DispatchContext.Counter = 0  # TODO: 不符合条件之后需要将标志位置为0

    except Exception as e:
        Logger.error(repr(e))
    """
        传统的方式去传递
        # json.dumps(字典)  将Python的字典转换为json的字符串
        # json.loads(字符串)  将字符串转换为Python中的字典
        json_str = json.dumps(data)
        # 改变，响应头的类型
        return json_str,200,{"Content-Type":"application/json"}
    """
    '''
        jsonify()的使用
        1.jsonify()帮助转为json数据，并设置响应头 Content-Type 为 application/json
        2. 可以不用提前构造好字典，直接返回,结果是一样的
            return jsonify(City="Beijing",age=20)
    '''
    return json.dumps(data1).encode("utf-8")




@app.route("/freqamp/")
def frecy_amp():  #返回原始信号数据的幅值以及震动频率
    """向前端返回json类型的数据  根据接收的型号 返回查询到数据"""
    #float(DispatchContext.frequency)
    data = {
        "frequency": 8.0,
        "Amplitude": 0.9 #TODO: 这里需要把 幅值的额计算逻辑 给计算出来
    }
    return json.dumps(data).encode("utf-8")



'''用于传输 悬臂梁当前的应力值'''
@app.route("/stress/", methods=["GET"])
def strss_map():
    Logger.info("strss_map response")
    data_stress = {
        "stressValue": 0.9  # TODO: 这里需要把 幅值的额计算逻辑 给计算出来
    }
    return json.dumps(data_stress).encode("utf-8")


'''用于警告记录'''
@app.route("/warnning/", methods=["GET"])
def warning_map():
    Logger.info("warning_map response!!")
    data_stress = {
        "warning_log": ["2023-11-29","2023-11-29","2023-11-29"]  # TODO: 这里需要把 幅值的额计算逻辑 给计算出来
    }
    return json.dumps(data_stress).encode("utf-8")




@app.route("/predictinfo/")
def Prediction():  #返回  预测值及类别
    """向前端返回json类型的数据  根据接收的型号 返回查询到数据"""
    try:
        print("DispatchContext.predict_info",DispatchContext.predict_info)
        if DispatchContext.data_seg[DispatchContext.Counter] != None and DispatchContext.Counter <= 319:
            data = {
                "location": DispatchContext.predict_info[DispatchContext.Counter],
                "category": "crack",
                "result":DispatchContext.predict_info[DispatchContext.Counter]
            }
    except Exception as e:
        Logger.error(repr(e))
    return json.dumps(data).encode("utf-8")

#unity interaction
@app.route("/beamstatus/")
def sendstatus():  #返回  预测值及类别
    """向前端返回json类型的数据  根据接收的型号 返回查询到数据"""

    data = {
        "beamstatus": DispatchContext.beam_status,
    }
    return json.dumps(data).encode("utf-8")



@app.route("/preacc/")
def accuracy():
    """向前端返回json类型的数据  根据接收的型号 返回查询到数据"""
    data = {
        "prevalue": DispatchContext.predict_info[DispatchContext.Counter],
    }
    return json.dumps(data).encode("utf-8")




# if __name__ == '__main__':

from InteractionLogic import work_loop #接收到数据 开始处理线程
try:
    thread_synchronize_data = threading.Thread(target=work_loop,
                                             name = 'synchronize')
    thread_synchronize_data.setDaemon(True)
    thread_synchronize_data.start()
    Logger.info("start a new thread to synchronize data.")
except Exception as e:
    Logger.error("when start a new thread to synchronize_data!")
    Logger.error(repr(e))
    ToolFunctions.sys_exit(104)



app.run(host='0.0.0.0',threaded=True, port=5006, debug=False)