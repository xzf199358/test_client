# -*- encoding: utf-8 -*-
'''
@File: InteractionLogic.py
@Author: Zifeng Xu
@Date: 2022/12/17 20:28
@license: Copyright(C),shanghai university
@contact: xuzifeng@shu.edu.cn
@software: pycharm
'''

from GlobalContext import *
from LoggerModule import Logger
import time


def work_loop():
    Logger.info('start interaction logic loop')
    from GlobalContext import DispatchContext
    while True:
        DispatchContext.all_lock.acquire()
        current_fre = DispatchContext.frequency
        current_loc = DispatchContext.location
        current_testtime = DispatchContext.test_time
        Logger.info('current information: ' + str(current_fre) + str(current_loc) + str(current_testtime))
        try:
            if current_fre!=None and current_loc != None and current_testtime != None:
                DispatchContext.load_selected_data()
                DispatchContext.frequency = None
                DispatchContext.location = None
                DispatchContext.test_time = None
            else:
                Logger.info(" the selected data conditions is empty ")
        except Exception as e:
            Logger.error('when execute dispatch logic!')
            Logger.error(repr(e))
        DispatchContext.all_lock.release()
        Logger.info('Thread for interaction logic keeps alive.')
        time.sleep(0.3)  # sleep time unit is second

















