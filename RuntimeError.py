# -*- coding: UTF-8 -*-
'''

@author: oShine <oyjqdlp@126.com>
@link: https://github.com/ouyangjunqiu/ou.py
异常处理
'''
class AppExitException(Exception):
    @staticmethod
    def sigterm_handler(signum, frame):
        raise AppExitException()

    pass