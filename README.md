## android 应用自动化程序
模拟器采用mumu模拟器，实现android批量处理部署等操作


### 安装必备

#### 环境
- 本地安装 Tesseract-OCR [下载地址](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe)
Tesseract-OCR下tessdata中具备 chi_sim.traineddata [训练模型文件](https://github.com/tesseract-ocr/tessdata/blob/main/chi_sim.traineddata) 
- python 3.9
- mumu模拟器12 [下载地址](https://a11.gdl.netease.com/MuMuInstaller_3.1.4.0_niesdc-mj22456-360-pcsem-dev_zh-Hans_1685675813.exe)
- adb  [下载地址](https://dl.google.com/android/repository/platform-tools_r34.0.5-windows.zip)


### 启动

#### 运行app

#### 具体参数 
- action 启动类型 
  - init 初始化部署app 
  - run 运行app
- 虚拟机数量 num
- 虚拟机初始端口 first

```shell

python main.py --action init --first 16384 --num 10

```
