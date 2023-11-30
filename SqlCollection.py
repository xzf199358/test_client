# -*- coding: UTF-8 -*-

import sys, os
from LoggerModule import Logger


class SqlCollection:
    get_selected_data = ''
    predict_density = ''
    confidence_info = ''

    @classmethod
    def load_sql_interfaces(cls):
        try:
            # 如果文件不是uft-8编码方式，读取文件可能报错
            cls.get_selected_data = cls.process_sql_file_special_character(open('sql/get_selected_data.sql', 'r', encoding='utf-8').read())
            # cls.predict_density = cls.process_sql_file_special_character(open('sql/insert_density.sql', 'r', encoding='utf-8').read())
            # cls.confidence_info = cls.process_sql_file_special_character(open('sql/insert_confidence_info.sql', 'r', encoding='utf').read())
            return 0
        except Exception as e:
            Logger.error('when SqlCollection.load_sql_interfaces()!')
            Logger.error(repr(e))
            return -1

    @classmethod
    def process_sql_file_special_character(cls, file_content: str) -> str:  # 由于postgres保存的sql开头有特殊字符，必须预处理一下，否则可能不被识别
        if file_content[0] == '\ufeff' or file_content[0] == '\ufffe':
            cut_content = file_content[1:]
            return cut_content
        else:
            return file_content

if __name__ == '__main__':

    SqlCollection.load_sql_interfaces()
    print(SqlCollection.predict_info)
    print(SqlCollection.predict_density)





