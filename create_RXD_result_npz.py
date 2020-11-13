# -*- coding: utf-8 -*-
"""
このファイルは　20/11/12(木) 23:57:53　作成されました

@author: Yuchi
"""

import numpy as np
import scipy.io as sio
import time
from sklearn.metrics import mean_squared_error
import warnings

'''
資料正規化

輸入
    input_data: 輸入資料，可以為1~3維array
輸出
    normal_data: 經過正規化的資料
'''
def data_normalize(input_data):
    input_data = np.array(input_data)*1.0
    maximum = np.max(np.max(input_data))
    minimum = np.min(np.min(input_data))
        
    normal_data = (input_data-minimum)/(maximum-minimum)*1.0
    return normal_data


'''
計算原版的R_RXD

輸入
    r     : 高光譜影像，2d-array，shape為[band數量, 點數量]
輸出
    result: 演算法結果，2d-array，shape為[點數量, 1]
    t     : 計算時間，float
    Rinv  : R的逆矩陣，2d-array，shape為[band數量, band數量]
'''
def R_RXD(r):
    start_time = time.perf_counter()
    rt = np.transpose(r)
    R = (1/(r.shape[1]))*(r@rt)
    
    try:
        Rinv = np.linalg.inv(R)
    except:
        Rinv = np.linalg.pinv(R)
        warnings.warn('pinv used')
        
    result = np.sum(((np.dot(rt, Rinv))*rt), 1)
    
    end_time = time.perf_counter()
    t = end_time-start_time
    return result, t, Rinv


'''
計算Woodbury版的R_RXD

輸入
    r     : 高光譜影像，2d-array，shape為[band數量, 1]
    Rinv  : 修正前的R的逆矩陣，2d-array，shape為[band數量, band數量]
    n     : 目前計算第n個點，int
輸出
    result: 演算法結果，2d-array，shape為[點數量, 1]
    t     : 計算時間，float
    Rinv  : 修正後的R的逆矩陣，2d-array，shape為[band數量, band數量]
'''
def Woodbury(r, Rinv, n):
    start_time = time.perf_counter()
    rt = np.transpose(r)
    v = (1/np.sqrt(n))*r
    Rinv = (Rinv-((np.dot(np.dot(Rinv, v), np.dot(np.transpose(v), Rinv)))/(1+(np.dot(np.dot(np.transpose(v), Rinv), v)))))
    
    result = rt@Rinv@r
    
    end_time = time.perf_counter()
    t = end_time-start_time
    return result, t, Rinv


'''主程式'''
if __name__ == '__main__':
    matfn='./panelHIM.mat' 
    Im=sio.loadmat(matfn) 
    Im=Im['HIM']
    Im = np.double(Im)
    Im = np.array(Im)
    Im = data_normalize(Im)
    r = np.transpose(np.reshape(Im, [-1, Im.shape[2]]))
    
    r_np_img = np.zeros([Im.shape[0]*Im.shape[1]])
    r_wb_img = np.zeros([Im.shape[0]*Im.shape[1]])
    np_all_t = []
    wb_all_t = []
    np_all_img = []
    wb_all_img = []
    all_MSE = []

    for i in range(4096):  
        print(f'{i+1}/4096======================================')
        '''計算原版的R_RXD'''
        np_rrxd, np_t, np_invR = R_RXD(r[:, 0:i+1])
        r_np_img[0:i+1] = np_rrxd
        np_img = np.reshape(r_np_img, [Im.shape[0], Im.shape[1]])
        
        '''儲存'''
        np_all_t.append(np_t)
        np_all_img.append(np_rrxd)       
        
        '''計算Woodbury版的R_RXD'''
        if i<169:  # 前169個點用原版的R_RXD計算
            wb_rrxd, wb_t, wb_invR = R_RXD(r[:, :i+1])     
            r_wb_img[0:i+1] = wb_rrxd
            wb_img = np.reshape(r_wb_img, [Im.shape[0], Im.shape[1]])
            wb = wb_rrxd.copy()  # wb是要儲存的
        else:  # 其他點用Woodbury版的R_RXD計算，一次計算一個點
            wb_rrxd, wb_t ,wb_invR = Woodbury(r[:, i:i+1], wb_invR, i)
            r_wb_img[i:i+1] = wb_rrxd
            wb_img = np.reshape(r_wb_img, [Im.shape[0], Im.shape[1]])
            wb = np.append(wb, wb_rrxd)  # wb是要儲存的
        
        '''儲存'''
        wb_all_t.append(wb_t)
        wb_all_img.append(wb)
        
        '''計算原版和Woodbury版結果的MSE並儲存'''
        mse = mean_squared_error(np_img, wb_img)
        all_MSE.append(mse)       
    print('done!')
    
    np.savez('res.npz', 
             np_all_t = np_all_t, np_all_img = np_all_img,
             wb_all_t = wb_all_t, wb_all_img = wb_all_img,
             all_MSE = all_MSE)
    
    '''看這個檔案的key'''
    x = np.load('res.npz')
    for k in x.iterkeys():
        print(k)