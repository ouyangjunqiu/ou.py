# -*- coding: UTF-8 -*-
"""

@author: oShine <oyjqdlp@126.com>
@link: https://github.com/ouyangjunqiu/ou.py
定时器，每隔一段时间执行一次
"""

import threading


class Timer(threading.Thread):
    def __init__(self, interval, function, args=[], kwargs={}):
        threading.Thread.__init__(self)

        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = threading.Event()
        self.daemon = True

    def run(self):
        while not self.finished.is_set():
            try:
                self.function(*self.args, **self.kwargs)
            except Exception, ex:
                self._note("Function:(%s),exception:(%r)", self.function, ex)
                pass
            self.finished.wait(self.interval)

    def close(self):
        self.finished.set()

    def terminate(self):
        self.close()
        self.join(self.interval*2)
