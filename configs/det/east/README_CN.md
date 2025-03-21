[English](README.md) | 中文

# EAST

<!--- Guideline: use url linked to abstract in ArXiv instead of PDF for fast loading.  -->

> [EAST: An Efficient and Accurate Scene Text Detector](https://arxiv.org/abs/1704.03155)

## 概述

### EAST

EAST (Efficient and Accurate Scene Text Detection)是一种高效、准确且轻量级的OCR检测算法，主要用于在自然场景下的文本检测。该算法使用深度残差网络提取文本特征，在特征金字塔网络中进行特征融合，并采用二分类和定位两个分支来检测文本。EAST在文本检测的准确性和鲁棒性方面取得了显著的成果。

<p align="center"><img alt="Figure 1. east_architecture" src="https://github.com/tonytonglt/mindocr/assets/54050944/4781c9aa-64a5-4963-bf02-6620d173dc9a" width="384"/></p>
<p align="center"><em>图 1. EAST整体架构图（我们使用ResNet50取代图中的PVANet）</em></p>

EAST的整体架构图如图1所示，包含以下阶段:

1.**特征提取**:
使用Resnet-50作为骨干网络，从2，3，4，5阶段进行不同层级的特征提取；

2.**特征融合**:
采用特征融合的方式，将骨干网络中不同层级的特征进行放大，并和更大的特征图沿通道轴进行连接，如此反复。使得模型可以对不同大小的文本区域进行处理，并提高检测的精度。

3.**边界框回归**:
对文本框的位置以及旋转角进行回归，使得EAST能够检测倾斜文本，完成自然场景下文本检测的任务。目前支持检测旋转矩形文本区域的文本框。

4.**文本分支**:
在确定了文本区域的位置和大小后，EAST模型会进一步将这些区域分类为文本或非文本区域。为此，模型采用了一条全卷积的文本分支，对文本区域进行二分类。

### 配套版本

| mindspore  | ascend driver  |    firmware    | cann toolkit/kernel |
|:----------:|:--------------:|:--------------:|:-------------------:|
|   2.5.0    |    24.1.0      |   7.5.0.3.220  |     8.0.0.beta1     |

## 快速上手

### 安装

请参考MindOCR套件的[安装指南](https://github.com/mindspore-lab/mindocr#installation) 。

### 数据准备

请从[该网址](https://rrc.cvc.uab.es/?ch=4&com=downloads)下载ICDAR2015数据集，然后参考[数据转换](https://github.com/mindspore-lab/mindocr/blob/main/tools/dataset_converters/README_CN.md)对数据集标注进行格式转换。

完成数据准备工作后，数据的目录结构应该如下所示：

``` text
.
├── test
│   ├── images
│   │   ├── img_1.jpg
│   │   ├── img_2.jpg
│   │   └── ...
│   └── test_det_gt.txt
└── train
    ├── images
    │   ├── img_1.jpg
    │   ├── img_2.jpg
    │   └── ....jpg
    └── train_det_gt.txt
```

### 配置说明

在配置文件`configs/det/east/east_r50_icdar15.yaml`中更新如下文件路径。其中`dataset_root`会分别和`dataset_root`以及`label_file`拼接构成完整的数据集目录和标签文件路径。

```yaml
...
train:
  ckpt_save_dir: './tmp_det'
  dataset_sink_mode: False
  dataset:
    type: DetDataset
    dataset_root: dir/to/dataset          <--- 更新
    data_dir: train/images                <--- 更新
    label_file: train/train_det_gt.txt    <--- 更新
...
eval:
  dataset_sink_mode: False
  dataset:
    type: DetDataset
    dataset_root: dir/to/dataset          <--- 更新
    data_dir: test/images                 <--- 更新
    label_file: test/test_det_gt.txt      <--- 更新
...
```

> 【可选】可以根据CPU核的数量设置`num_workers`参数的值。



EAST由3个部分组成：`backbone`、`neck`和`head`。具体来说:

```yaml
model:
  type: det
  transform: null
  backbone:
    name: det_resnet50
    pretrained: True    # 是否使用ImageNet数据集上的预训练权重
  neck:
    name: EASTFPN       # EAST的特征金字塔网络
    out_channels: 128
  head:
    name: EASTHead
```

### 训练

* 单卡训练

请确保yaml文件中的`distribute`参数为False。

``` shell
# train east on ic15 dataset
python tools/train.py --config configs/det/east/east_r50_icdar15.yaml
```

* 分布式训练

请确保yaml文件中的`distribute`参数为True。

```shell
# worker_num代表分布式总进程数量。
# local_worker_num代表当前节点进程数量。
# 进程数量即为训练使用的NPU的数量，单机多卡情况下worker_num和local_worker_num需保持一致。
msrun --worker_num=8 --local_worker_num=8 python tools/train.py --config configs/det/east/east_r50_icdar15.yaml

# 经验证，绑核在大部分情况下有性能加速，请配置参数并运行
msrun --bind_core=True --worker_num=8 --local_worker_num=8 python tools/train.py --config configs/det/east/east_r50_icdar15.yaml
```
**注意:** 有关 msrun 配置的更多信息，请参考[此处](https://www.mindspore.cn/docs/zh-CN/master/model_train/parallel/msrun_launcher.html).

训练结果（包括checkpoint、每个epoch的性能和曲线图）将被保存在yaml配置文件的`ckpt_save_dir`参数配置的路径下，默认为`./tmp_det`。

### 评估

评估环节，在yaml配置文件中将`ckpt_load_path`参数配置为checkpoint文件的路径，设置`distribute`为False，然后运行：

``` shell
python tools/eval.py --config configs/det/east/east_r50_icdar15.yaml
```

### MindSpore Lite 推理

请参考[MindOCR 推理](../../../docs/zh/inference/inference_tutorial.md)教程，基于MindSpore Lite在Ascend 310上进行模型的推理，包括以下步骤：

- 模型导出

请先[下载](#2-实验结果)已导出的MindIR文件，或者参考[模型导出](../../../docs/zh/inference/convert_tutorial.md#1-模型导出)教程，使用以下命令将训练完成的ckpt导出为MindIR文件:

``` shell
python tools/export.py --model_name_or_config east_resnet50 --data_shape 720 1280 --local_ckpt_path /path/to/local_ckpt.ckpt
# or
python tools/export.py --model_name_or_config configs/det/east/east_r50_icdar15.yaml --data_shape 720 1280 --local_ckpt_path /path/to/local_ckpt.ckpt
```

其中，`data_shape`是导出MindIR时的模型输入Shape的height和width，下载链接中MindIR对应的shape值见[注释](#注释)。

- 环境搭建

请参考[环境安装](../../../docs/zh/inference/environment.md)教程，配置MindSpore Lite推理运行环境。

- 模型转换

请参考[模型转换](../../../docs/zh/inference/convert_tutorial.md#2-mindspore-lite-mindir-转换)教程，使用`converter_lite`工具对MindIR模型进行离线转换。


- 执行推理

假设在模型转换后得到output.mindir文件，在`deploy/py_infer`目录下使用以下命令进行推理：

```shell
python infer.py \
    --input_images_dir=/your_path_to/test_images \
    --det_model_path=your_path_to/output.mindir \
    --det_model_name_or_config=../../configs/det/east/east_r50_icdar15.yaml \
    --res_save_dir=results_dir
```

## 性能表现

EAST在ICDAR2015数据集上训练。另外，我们在ImageNet数据集上进行了预训练，并提供预训练权重下载链接。所有训练结果如下：

### ICDAR2015

| **model name** | **backbone** | **pretrained** | **cards** | **batch size** | **jit level** | **graph compile** | **ms/step** | **img/s** | **recall** | **precision** | **f-score** |              **recipe**               |                                           **weight**                                          |
|:--------------:|:------------:| :------------: |:---------:|:--------------:| :-----------: |:-----------------:|:-----------:|:---------:|:----------:|:-------------:|:-----------:|:-------------------------------------:|:---------------------------------------------------------------------------------------------:|
|      EAST      | ResNet-50    |    ImageNet    |     8     |       20       |      O2       |     250.32 s      |   254.54    |  628.58   |   80.36%   |    84.17%     |   82.22%    |   [yaml](east_r50_icdar15.yaml)       | [ckpt](https://download.mindspore.cn/toolkits/mindocr/east/east_resnet50_ic15-7262e359.ckpt) \| [mindir](https://download.mindspore.cn/toolkits/mindocr/east/east_resnet50_ic15-7262e359-5f05cd42.mindir)   |
|      EAST      | MobileNetV3  |    ImageNet    |     8     |       20       |      O2       |     313.78 s      |    91.59    |  1746.92  |   73.18%   |    74.07%     |   73.63%    | [yaml](east_mobilenetv3_icdar15.yaml) |[ckpt](https://download.mindspore.cn/toolkits/mindocr/east/east_mobilenetv3_ic15-4288dba1.ckpt) \| [mindir](https://download.mindspore.cn/toolkits/mindocr/east/east_mobilenetv3_ic15-4288dba1-5bf242c5.mindir)|

#### 注释：
- EAST的训练时长受数据处理部分和不同运行环境的影响非常大。
- 链接中MindIR导出时的输入Shape为`(1,3,720,1280)` 。

## 参考文献

<!--- Guideline: Citation format GB/T 7714 is suggested. -->

[1] Xinyu Zhou, Cong Yao, He Wen, Yuzhi Wang, Shuchang Zhou, Weiran He, Jiajun Liang. EAST: An Efficient and Accurate Scene Text Detector. arXiv:1704.03155, 2017
