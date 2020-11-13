# RXD-GUI  

## 如何使用  
0. 載、都可以載  
```bash
$ git clone https://github.com/ek2061/RXD-GUI  
$ cd RXD-GUI  
```

1. 取得高光譜影像mat  
panelHIM.mat戰車圖這個自己想辦法了啦  

2. 取得計算RXD的結果(.npz)  
```bash
python create_RXD_result_npz.py  
```
會拿到res.npz  

3. 執行  
```bash
python RXD_app.py  
```
打開以後會看到2個可以選檔案的  
HSI image  (.mat)選panelHIM.mat戰車圖  
RXD result (.npz)選剛剛產生的res.npz  
