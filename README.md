# RXD-GUI  

## 如何使用  
0. 載、都可以載  
```bash=
$ git clone https://github.com/ek2061/RXD-GUI  
$ cd RXD-GUI  
```

1. 取得高光譜影像mat檔  
panelHIM.mat戰車圖這個自己想辦法了啦  

2. 計算RXD的結果並存成npz檔(得到res.npz)  
```bash=
$ python create_RXD_result_npz.py  
```

3. 執行app打開GUI介面  
```bash=
$ python RXD_app.py  
```
打開以後會看到2個可以選檔案的  
HSI image  (.mat)選panelHIM.mat戰車圖  
RXD result (.npz)選剛剛產生的res.npz  

## 執行檔連結
https://www.asuswebstorage.com/navigate/a/#/s/3CD361086D92488FADD2D26D38C0DA27Y
1. res.npz
我自己先跑過的計算結果
2. RXD-app.exe
把程式包成exe，在win10 64位元環境應該都能直接執行不用裝python

## QA
1. 為什麼要先計算完再畫圖?
A: 因為原本平行時執行各佔一半效能(?)，但在Woodbury算完後，Origin會拿到Woodbury釋放的效能進而加快計算速度，這樣不符合真實情況，所以先算完再依照計算時間的200倍畫圖。

2. 為什麼畫圖速度調慢200倍?
A: 因為計算速度太快了，以Woodbury為例，照原始時間0.00008秒畫每張圖，電腦絕對當掉。

3. 為什麼Origin方法那麼慢?
A: 那是正常速度，Origin和Woodbury速度本來就差很多，才第400點的計算時間就已經相差10倍。

4. 剛按Run RXD按鈕時很卡
A: 正常，因為電腦還沒調整好同時執行的效能，大概5秒後就會正常畫圖，還有那顆按鈕不能連續按2次，電腦會當掉。

## 其他
1. 調整畫圖速度
修改**call_originalRXD.py**和**call_woodburyRXD.py**，注意調太小會快到電腦當掉
```python=
 def run(self):
        result = {'img': 0}
        try:
            for i in range(4096):
                time.sleep(self.all_t[i]*200)  # 200是減速倍率，越大越慢
```

2. 想改成算K_RXD或其他演算法
修改create_RXD_result_npz.py裡的函式**R_RXD**和**Woodbury**

