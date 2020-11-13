# -*- coding: utf-8 -*-
"""
このファイルは　20/11/13(金) 01:34:46　作成されました

@author: Yuchi
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QSizePolicy, QMessageBox
from PyQt5.QtCore import QCoreApplication
from RXD_GUI import Ui_MainWindow

import numpy as np
import scipy.io as sio

import matplotlib
matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

'''call多線程'''
from PyQt5.Qt import QThreadPool
from call_originalRXD import Run_OriginalRXD
from call_woodburyRXD import Run_WoodburyRXD

'''滿版Figure，適合畫不需要刻度的圖'''
class FullFigure(FigureCanvas):
    def __init__(self,parent=None,width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0,wspace=0)
        self.axes = self.fig.add_subplot(111)
        self.axes.margins(0, 0)
        self.axes.hold(True)
        FigureCanvas.__init__(self,self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

'''縮版Figure，適合畫需要刻度的圖'''   
class InwardFigure(FigureCanvas):
    def __init__(self,parent=None,width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.margins(0, 0)
        self.axes.hold(True)
        FigureCanvas.__init__(self,self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        '''原圖Figure'''
        self.fig_img = FullFigure(width=5, height=4, dpi=100)
        self.fig_img.axes.axis('off')
        self.ui.verticalLayout.addWidget(self.fig_img)
        
        '''原始方法RXD Figure'''
        self.fig_original = FullFigure(width=5, height=4, dpi=100)
        self.fig_original.axes.axis('off')
        self.ui.verticalLayout_2.addWidget(self.fig_original)
        
        '''Woodbury方法RXD Figure'''
        self.fig_woodbury = FullFigure(width=5, height=4, dpi=100)
        self.fig_woodbury.axes.axis('off')
        self.ui.verticalLayout_3.addWidget(self.fig_woodbury)   
        
        '''時間Figure'''
        self.fig_time = InwardFigure(width=5, height=4, dpi=100)
        self.fig_time.axes.set_xlim(0, 4096)
        self.fig_time.axes.set_title('Cost time Original vs Woodbury')
        self.fig_time.axes.set_ylabel('Time(sec)')
        self.ui.verticalLayout_4.addWidget(self.fig_time)
        
        '''MSE Figure'''
        self.fig_mse = InwardFigure(width=5, height=4, dpi=100)
        self.fig_mse.axes.set_xlim(0, 4096)
        self.fig_mse.axes.set_title('MSE Original vs Woodbury')
        self.ui.verticalLayout_5.addWidget(self.fig_mse)
        
        '''按鈕連結事件'''
        self.ui.pushButton.clicked.connect(self.pushButton_Click)
        self.ui.pushButton_2.clicked.connect(self.pushButton_2_Click)
        self.ui.pushButton_3.clicked.connect(self.pushButton_3_Click)
        self.ui.pushButton_4.clicked.connect(self.pushButton_4_Click)
        
        self.show()
        
    '''載入高光譜影像並繪製原圖'''
    def pushButton_Click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select MAT File", "", "MAT Files (*.mat)", options=options)
        
        if fileName == '':
            QMessageBox.about(self, '請選擇mat檔')
        else:
            self.ui.lineEdit.setText(fileName)
            img = sio.loadmat(fileName)['HIM']
            self.fig_img.axes.clear()
            self.fig_img.axes.axis('off')
            self.fig_img.axes.imshow(img[:, :, 100], 'gray')    
            self.fig_img.draw()
            self.ui.verticalLayout.addWidget(self.fig_img)
    
    '''載入儲存好的RXD結果'''
    def pushButton_2_Click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select NPZ File", "", "MAT Files (*.npz)", options=options)
         
        if fileName == '':
            QMessageBox.about(self, '請選擇npz檔')
        else:
            self.ui.lineEdit_2.setText(fileName)
    
    def pushButton_3_Click(self):
        filename = self.ui.lineEdit_2.text()
        res = np.load(filename)
        
        np_all_img = res['np_all_img']    
        wb_all_img = res['wb_all_img']
        np_all_t = res['np_all_t']
        wb_all_t = res['wb_all_t']
        
        '''原始方法RXD多線程'''
        do_originalRXD = Run_OriginalRXD(np_all_img, np_all_t)  # 傳變數給多線程
        do_originalRXD.res.callback_signal.connect(self.drawOriginalRXD)  # 將回傳的變數連結給函式處理
        QThreadPool.globalInstance().start(do_originalRXD)  # 多線程開始工作
        
        '''Woodbury方法RXD多線程'''
        do_woodburyRXD = Run_WoodburyRXD(wb_all_img, wb_all_t)  # 傳變數給多線程
        do_woodburyRXD.res.callback_signal.connect(self.drawWoodburyRXD)  # 將回傳的變數連結給函式處理
        QThreadPool.globalInstance().start(do_woodburyRXD)  # 多線程開始工作
        
    
    '''畫原始方法和Woodbury方法RXD的時間和MSE'''
    def pushButton_4_Click(self):
        filename = self.ui.lineEdit_2.text()
        res = np.load(filename)
        
        '''畫時間圖'''
        np_all_t = res['np_all_t']
        wb_all_t = res['wb_all_t']
        self.fig_time.axes.clear()
        self.fig_time.axes.plot(np_all_t*1000, 'r', label='Original')
        self.fig_time.axes.plot(wb_all_t*1000, 'b', label='Woodbury')
        self.fig_time.axes.set_xlim(0, 4096)
        self.fig_time.axes.set_title('Cost time Original vs Woodbury')
        self.fig_time.axes.set_ylabel('Time(ms)')
        self.fig_time.axes.legend()
        self.fig_time.draw()
        self.ui.verticalLayout_4.addWidget(self.fig_time)
        
        '''畫MSE圖'''
        all_MSE = res['all_MSE']
        self.fig_mse.axes.clear()
        self.fig_mse.axes.plot(all_MSE, 'g')
        self.fig_mse.axes.set_xlim(0, 4096)
        self.fig_mse.axes.set_title('MSE Original vs Woodbury')
        self.fig_mse.draw()
        self.ui.verticalLayout_5.addWidget(self.fig_mse)
    
    '''使用原始方法RXD後續畫圖'''
    def drawOriginalRXD(self, msg, result):
        if msg == 'error':
            QMessageBox.about(self, '發生錯誤')
        else:
            img = result['img']
            self.fig_original.axes.clear()
            self.fig_original.axes.axis('off')
            self.fig_original.axes.imshow(img, cmap='gray', vmin=0, vmax=255)    
            self.fig_original.draw()
            self.ui.verticalLayout_2.addWidget(self.fig_original)
    
    '''使用Woodbury方法RXD後續畫圖'''
    def drawWoodburyRXD(self, msg, result):
        if msg == 'error':
            QMessageBox.about(self, '發生錯誤')
        else:
            img = result['img']
            self.fig_woodbury.axes.clear()
            self.fig_woodbury.axes.axis('off')
            self.fig_woodbury.axes.imshow(img, cmap='gray', vmin=0, vmax=255)    
            self.fig_woodbury.draw()
            self.ui.verticalLayout_3.addWidget(self.fig_woodbury)   
            

app = QCoreApplication.instance()
if app is None:
    app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())
