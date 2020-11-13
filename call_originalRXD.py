# -*- coding: utf-8 -*-
"""
このファイルは　20/11/13(金) 12:36:09　作成されました

@author: Yuchi
"""

import numpy as np
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
import time

'''返信内容格式'''
class ResponseSignals(QObject):
    callback_signal= pyqtSignal(str, dict)

class Run_OriginalRXD(QRunnable):
    def __init__(self, all_img, all_t):  # 前2個變數是主程式傳進來的
        super(QRunnable,self).__init__()
        self.all_img = all_img
        self.all_t = all_t
        self.res = ResponseSignals()

    def run(self):
        result = {'img': 0}
        try:
            for i in range(4096):
                time.sleep(self.all_t[i]*200)
                img = np.zeros(4096)
                img[0:i+1] = self.all_img[i]
                result['img'] = img.reshape([64, 64])
                self.res.callback_signal.emit('doing', result)
        except:
            self.res.callback_signal.emit('error', {})