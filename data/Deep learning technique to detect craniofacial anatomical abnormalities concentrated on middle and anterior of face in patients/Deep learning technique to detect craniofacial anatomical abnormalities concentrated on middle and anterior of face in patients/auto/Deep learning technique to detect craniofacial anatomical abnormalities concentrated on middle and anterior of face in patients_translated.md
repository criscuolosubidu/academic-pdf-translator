# 深度学习技术检测睡眠呼吸暂停患者面部中前部颅面解剖异常

帅何 a,1, , 李英杰 b,1, 张冲, 李祖飞 a, 任媛媛 a, 李天成 * a, ,  
王建廷 a **

a 首都医科大学附属北京朝阳医院耳鼻咽喉头颈外科，中国  
b 北京工商大学计算机科学与工程学院，中国  
c 清华大学自动化系，中国

# 文章信息 (ARTICLEINFO)

# 摘要 (ABSTRACT)

关键词：可解释深度学习（Explainable deep learning） 颅面照片（Craniofacial photographs） 阻塞性睡眠呼吸暂停（Obstructive sleep apnea）

研究目的：本研究旨在提出一种基于深度学习（deep learning）的模型，利用颅面部（craniofacial）照片进行自动阻塞性睡眠呼吸暂停（obstructive sleep apnea, OSA）检测，并通过设计可解释性测试来探究关键的颅面部区域以及该方法的可靠性。

方法：对530名疑似阻塞性睡眠呼吸暂停（OSA）的参与者进行多导睡眠监测（polysomnography）。采集正面与侧面颅面照片，并随机划分为训练集、验证集和测试集，用于模型开发与评估。通过照片遮挡测试与视觉观察确定OSA风险区域。统计每位参与者的阳性区域数量，并评估其与OSA的关联性。

结果：仅使用颅面照片的模型准确率为0.884，受试者工作特征曲线下面积为0.881（95%置信区间为0.839-0.922）。采用敏感度与特异度之和最大化的截断点时，该模型显示出0.905的敏感度与0.941的特异度。双侧眼区、鼻唇颏区、耳前区及耳部对疾病检测贡献度最高。当使用增强这些区域权重的照片时，模型性能得到提升。此外，随着阳性颅面区域数量的增加，不同严重程度的阻塞性睡眠呼吸暂停（OSA）患病率呈现上升趋势。

结论：研究结果表明，基于深度学习（deep learning）的模型能够提取出主要集中在面部中前区域的有意义特征。

# 1． 引言 (Introduction)

阻塞性睡眠呼吸暂停（Obstructive Sleep Apnea, OSA）是一种常见的睡眠障碍，据估计影响约9.36亿成年人[1]。该病症的特征是反复出现的气流停止和减少，导致间歇性低氧血症、交感神经激活和睡眠碎片化[2]。OSA会引起多种日间和夜间症状，如过度嗜睡、打鼾、目击性呼吸暂停以及健康相关生活质量的下降。此外，OSA与心血管、代谢及神经认知功能障碍呈负相关[3,4]。因此，早期诊断和有效管理对于预防不良健康结局至关重要。

颅面骨骼尺寸受限、上气道软组织增大以及局部脂肪组织过多，均可能影响上气道管腔空间，从而使其在睡眠期间更易发生塌陷。放射影像技术，如头颅侧位X线摄影（cephalometric radiography）、上气道计算机断层扫描（CT）以及上气道磁共振成像（MRI），已被用于二维（2D）或三维（3D）分析，以量化骨骼与软组织特征，并识别阻塞性睡眠呼吸暂停（OSA）的特定解剖风险因素。较大的舌体体积、较厚的咽侧壁、较厚的软腭、位置偏下偏后的舌骨，以及较短的下颌骨、上颌骨和颅底长度，均可增加睡眠呼吸暂停的风险[5-7]。然而，由于这些影像技术操作繁琐、存在辐射暴露风险且需要特定设备，通常仅限于研究应用。

定量摄影分析已被提出作为一种替代评估技术，用于阐明颅面形态与睡眠呼吸暂停之间的关系。早期研究使用标准正面和侧面面部校准照片、手动标注和测量，证明了阻塞性睡眠呼吸暂停（OSA）患者存在一系列明显的颅面特征。此外，摄影测量在白种人和中国成年人的OSA风险分层和筛查中可能具有临床实用性[8,9]。然而，图像的手动标注和摄影测量可能耗时且存在阅片者间差异。为缓解这一问题，可采用基于深度学习（deep learning）的模型以自学习方式捕捉原始图像中隐藏的重要特征，从而避免手动标注和特征计算的必要性[10]。在此过程中，输入图像流经多层神经网络以学习数据特征，并输出各类别的概率。先前，我们提出了一种基于深度卷积神经网络（deep convolutional neural network）和五角度颅面照片的预测模型，该模型能够区分患有和未患OSA的个体（受试者工作特征曲线下面积（AUC）为0.9）[11]。然而，在将该模型应用于真实临床环境前，需要一定程度的可解释性以获得临床医生和患者的信任。在当前研究中，我们进行了多项测试以考察重要的颅面区域，并使深度学习算法更加透明和易于理解。我们假设基于深度学习的模型能够从不同颅面区域识别与OSA相关的特征，并且通过增加区域特征的权重可以提高预测效率。

# 2. 方法 (Methods)

# 2.1． 研究对象 (Participants)

年龄超过18岁、因疑似阻塞性睡眠呼吸暂停（OSA）而首次转诊至北京朝阳医院耳鼻咽喉头颈外科睡眠中心的参与者被连续招募，并随机分为训练集、验证集和测试集，用于模型的开发与评估。排除标准包括：存在先天性或获得性颅面畸形、多导睡眠监测（PSG）中中枢性呼吸暂停和/或中枢性低通气事件≥5次/小时且占呼吸事件总数≥50%、以及面部毛发过多。所有参与者均签署书面知情同意书，本研究已获得北京朝阳医院伦理委员会的批准。

# 2.2. 数据采集 (Data acquisition)

颅面摄影方案与我们先前研究[11]所用方法一致。简言之，在受试者保持自然头位、双眼睁开状态下采集面部正位与侧位照片。正位照片覆盖范围从头顶及耳部上缘至环状软骨水平区域。侧位照片则涵盖鼻部、头顶、枕部至环状软骨水平区域。同时记录临床变量，包括性别、年龄（岁）、体重指数（BMI，kg/m²）及颈围（cm）。

所有受试者均接受了夜间多导睡眠监测（Embla N7000, RemLogic Eastmed），监测项目包括脑电图、眼电图、心电图、颏肌电图、鼻压力传感、胸腹呼吸感应体积描记及脉搏血氧测定。睡眠事件与呼吸事件由技术人员根据美国睡眠医学会标准[12]进行判读。随后，根据呼吸努力的存在情况，将呼吸暂停与低通气事件分为中枢性、阻塞性或混合性三类。呼吸暂停低通气指数通过每小时睡眠中呼吸暂停与低通气事件总数计算得出。阻塞性睡眠呼吸暂停的诊断依据三个阈值界定：AHI ≥ 5 次/小时、AHI ≥ 15 次/小时及 AHI ≥ 30 次/小时。本研究算法采用这三个阈值进行训练与测试，以预测不同严重程度的阻塞性睡眠呼吸暂停。

# 2.3. 模型开发 (Model development)

由于原始照片尺寸不统一，不适合直接作为深度神经网络（deep neural networks）的输入。因此，我们使用OpenCV（一个于2000年首次发布的开源计算机视觉库）的预训练函数对照片进行了预处理[13]。该库能够识别并裁剪正面和侧面人脸图像，通过边界框坐标生成统一尺寸的照片（512×512像素）。正面与侧面视图的不同特征相互补充，提供了有效信息。根据多导睡眠图（PSG）得出的呼吸暂停低通气指数（AHI）阈值（≥5次/小时、15次/小时或30次/小时），数据被分为阻塞性睡眠呼吸暂停（OSA）病例组和对照组。随后，按7:1:2的比例随机划分为训练集、验证集和测试集。训练集和验证集用于训练网络层并确定最优参数，测试集样本则用于评估模型性能及识别影响输出的关键区域。该随机方法的详细说明可见文献[11]。

在我们的研究中，阻塞性睡眠呼吸暂停（OSA）预测是一个二分类问题，分类过程包含两个阶段：1.特征提取和2.分类。我们应用深度卷积神经网络（Deep Convolutional Neural Networks）来学习判别性特征。在第一阶段，通过图像编码器（image encoder）识别并融合每位参与者两张颅面照片和四项临床变量（性别、年龄、身体质量指数（BMI）和颈围）中隐含的重要特征，生成维度特征图。图像编码器以ResNet-101作为主干网络（backbone），包含四个不同的模块。这些模块的卷积层（convolutional layers）具有不同的通道尺度、卷积核尺寸（kernel sizes）和步长（strides）。较低层级学习图像的基本形状和边缘等基础特征，随后由更高层级以更抽象的方式进行进一步处理。在此过程中，从输入的颅面照片中识别出更复杂的特征，同时过滤掉无关特征。卷积层之后引入平均池化层（average pooling）和最大池化层（maximum pooling）以降低特征图维度，从而减少参数量。在第二阶段，高级特征图通过全连接层（fully connected layers）和线性整流单元（ReLu）传递，最终经由softmax函数计算疾病发生概率（详见补充材料）。图1展示了使用颅面照片进行OSA分类的深度神经网络架构。通过对比初始层的低阶特征与最终层的高阶特征可以发现，具有鉴别性的面部特征逐渐显现，而与身份相关的特征则逐渐消失。

基于深度学习（deep learning）的模型首先在训练集（training set）上进行拟合；同时，验证集（validation set）用于评估模型性能并实现超参数（hyperparameter）调优。通过将模型预测的概率与基于多导睡眠监测（PSG）的金标准（ground truth）进行对比，计算预测误差，并据此调整参数以降低误差。在本研究中，模型训练采用随机梯度下降（stochastic gradient descent）方法，使用Adam优化器（Adam optimizer），基础学习率（base learning rate）为$10^{-3}$，批次大小（batch size）为64，动量（momentum）为0.9，权重衰减（weight decay）为0.0005，共进行300轮（epochs）训练。训练完成后，算法参数被锁定。

模型开发与预处理流程基于Python 3.7.16和PyTorch 1.12.1实现。

![](images/f15254739e8f5520960754b6895f2606d5c311b08096e9cad6d7fb33940c071e.jpg)

b

![](images/94e56e6bb51830133bfcca77c9228158a0a28148ffefa36b796997bdfc59c09e.jpg)

![](images/42be7ee9cbc8940040b7a329bfd2e32c706b923e3e42f0656396d4af239580e7.jpg)  
图1.基于深度学习的分类器示意图。(a)原始颅面照片转换为特征向量。特征图 $(1028 \times 1)$ 通过神经网络传递。

# 2.4. 模型评估与统计分析

模型性能通过在测试集上计算准确率、AUC曲线、敏感度和特异度进行评估，其中阈值点选自受试者工作特征曲线。

数据以均值±标准差或中位数（四分位距）表示连续变量，以百分比表示分类变量。采用Student's t检验和Mann-Whitney U检验比较正态分布与偏态分布的连续变量，分类变量采用卡方检验进行组间比较。设定P<0.05为具有统计学意义。所有统计分析均使用SPSS（版本22.0）软件完成。

# 2.5. 关于模型的讨论

许多基于深度学习（deep learning）的模型无法明确解释其预测结果，也无法提供有助于分类的面部区域信息。因此，我们进行了多项测试，以更好地理解模型并提升其准确性。

# 2.6. 摄影遮挡（Photographic occlusion）

我们在测试集中对九组额面和侧面颅面照片进行了遮挡处理，使用黑色补丁（RGB,(0,0,0)）覆盖以下区域：前额、双侧眼睛、鼻子、双侧面颊、口唇与下颌、耳部、耳前区、颞枕区及颈部（图2）。随后，将遮挡后的颅面照片输入模型，并通过比较其受试者工作特征曲线下面积（AUC）相较于原始照片的下降幅度，量化不同颅面区域对模型预测的贡献度。

此外，我们计算了正面和侧面照片贡献度的平均值。将贡献度未超过平均值的区域用黑色斑块遮挡，以增强网络视角中与阻塞性睡眠呼吸暂停（OSA）相关的信息。通过对遮挡照片与原始照片进行线性融合，生成了新加权的颅面照片。我们检验了加权照片是否能提升模型性能。

# 2.7. 视觉解释 (Visual Explanation)

为了直观解释网络所关注的图像区域，我们生成了显著图（saliency maps）以展示照片中重要的颅面特征。该显著图生成技术采用基于反向传播（backpropagation）的方法，突出显示对决策产生更大影响的像素[14]。我们基于预测概率最高和最低的30名参与者的平均值创建了显著图。

![](images/9efd9548c87516c8aa9e3b1ef16106973a3d0251aa5207e081994f7027ea7125.jpg)  
图2. 九种不同颅面区域遮挡示例。

# 2.8. 阻塞性睡眠呼吸暂停（OSA）阳性区域与严重程度的关系

为进一步探究颅面特征与阻塞性睡眠呼吸暂停（OSA）之间的关联，我们在测试集中评估了阳性颅面区域与OSA严重程度的关系。如前所述，我们对参与者正面及侧面照片的九个区域（如颈部、眼部、鼻部）进行了遮挡处理。若某区域被遮挡后模型预测概率较未遮挡时降低，则该区域被定义为阳性区域。针对每位参与者，我们统计其阳性区域数量，将其分为两组（0-4个或5-9个阳性区域），并采用不同呼吸暂停低通气指数（AHI）阈值比较两组人群的OSA患病率差异。

# 3. 结果 (Results)

# 3.1. 参与者特征

本研究共纳入530名符合纳入标准的参与者，其中女性占23.3%。总体而言，呼吸暂停低通气指数（AHI）处于0-5次/小时、5-15次/小时、15-30次/小时及≥30次/小时的参与者比例分别为21.7%、19.7%、14.9%和43.7%。参与者的平均年龄、体重指数（BMI）和颈围分别为40.55±11.86岁、27.03±4.42 kg/m²和

$3 9 . 8 3 \pm 4 . 1 8 \mathrm { c m }$ ,respectively.

受试者被随机分为训练集（N = 371）、验证集（N = 53）和测试集（N = 106）。表1总结了不同集合中研究人群特征的比较。三组在年龄、性别、体重指数（BMI）、呼吸暂停低通气指数（AHI）和阻塞性睡眠呼吸暂停（OSA）状态方面均未显示出统计学显著差异。

# 3.2. 模型性能

测试集的AUC（Area Under the Curve，曲线下面积）、灵敏度（sensitivity）、特异度（specificity）及准确度（accuracy）汇总于表2。当以呼吸暂停低通气指数（Apnea-Hypopnea Index, AHI）≥5次/小时作为阻塞性睡眠呼吸暂停（Obstructive Sleep Apnea, OSA）的诊断标准时，基于照片建立的预测模型取得了最佳性能，其准确度和AUC分别为0.884和0.881（95%置信区间[CI]：0.839-0.922）。采用灵敏度与特异度之和最大化的截断点（cutoff point）时，该模型的灵敏度为0.905，特异度为0.941。研究结果显示，相较于AHI阈值为5次/小时的标准，当采用AHI≥15次/小时作为阈值时，模型的准确度和AUC分别下降至0.878和0.872（95% CI：0.818-0.924）；当采用AHI≥30次/小时作为阈值时，则进一步降至0.874和0.853（95% CI：0.815-0.904）。当结合照片与临床变量进行预测时，模型诊断OSA的准确度得到进一步提升。

表1 参与者特征（Participant characteristics）

<table><tr><td></td><td>Variables</td><td>Training (N= 371)</td><td>Validation (N= 53)</td><td>P-valuea</td><td>Test (N= 106)</td><td>P-valueb</td></tr><tr><td rowspan="6">AHI≥5/h</td><td>Sex (M:F)</td><td>283:88</td><td>40:13</td><td>0.51</td><td>84:22</td><td>0.79</td></tr><tr><td>Age (years)</td><td>40.23 ± 11.85</td><td>41.53 ± 12.53</td><td>0.51</td><td>41.01 ± 11.76</td><td>0.60</td></tr><tr><td>NC (cm)</td><td>39.79 ± 4.23</td><td>39.89 ± 3.14</td><td>0.87</td><td>39.93 ± 4.51</td><td>0.95</td></tr><tr><td>BMI (kg/m²)</td><td>26.75 ± 4.47</td><td>27.07 ± 3.16</td><td>0.51</td><td>26.81 ± 4.89</td><td>0.78</td></tr><tr><td>Participants with OSA (%)</td><td>77.9</td><td>79.2</td><td>0.49</td><td>78.3</td><td>0.97</td></tr><tr><td>AHI (events/h)</td><td>22.1 (7.1,53.5)</td><td>29.1 (8.6,57.4)</td><td>0.49</td><td>20.6 (7.3,51.2)</td><td>0.72</td></tr><tr><td rowspan="6">AHI≥15/h</td><td>Sex (M:F)</td><td>289:82</td><td>39:14</td><td>0.49</td><td>79:27</td><td>0.41</td></tr><tr><td>Age (years)</td><td>40.32 ± 11.60</td><td>40.42 ± 12.91</td><td>0.99</td><td>41.25 ± 12.42</td><td>0.85</td></tr><tr><td>NC (cm)</td><td>39.86 ± 4.18</td><td>39.65 ± 4.11</td><td>0.93</td><td>39.80 ± 4.27</td><td>0.90</td></tr><tr><td>BMI (kg/m²)</td><td>26.71 ± 4.47</td><td>26.90 ± 4.23</td><td>0.56</td><td>27.03 ± 4.46</td><td>0.71</td></tr><tr><td>Participants with OSA (%)</td><td>58.5</td><td>58.5</td><td>0.56</td><td>58.5</td><td>0.53</td></tr><tr><td>AHI (events/h)</td><td>22.1 (7.2,53.7)</td><td>20.7 (5.9,38.8)</td><td>0.45</td><td>22.9 (7.2,55.4)</td><td>0.60</td></tr><tr><td rowspan="6">AHI ≥30/h</td><td>Sex (M:F)</td><td>283:88</td><td>38:15</td><td>0.28</td><td>86:20</td><td>0.38</td></tr><tr><td>Age (years)</td><td>40.21 ± 11.91</td><td>41.43 ± 10.62</td><td>0.41</td><td>41.13 ± 12.45</td><td>0.65</td></tr><tr><td>NC (cm)</td><td>39.81 ± 4.37</td><td>40.11 ± 3.63</td><td>0.56</td><td>39.74 ± 3.76</td><td>0.84</td></tr><tr><td>BMI (kg/m²)</td><td>26.86 ± 4.72</td><td>26.83 ± 3.60</td><td>0.72</td><td>26.54 ± 3.76</td><td>0.92</td></tr><tr><td>Participants with OSA (%)</td><td>43.4</td><td>45.3</td><td>0.45</td><td>43.4</td><td>0.96</td></tr><tr><td>AHI (events/h)</td><td>21.9 (6.4,54.5)</td><td>19.5 (8.2, 52.1)</td><td>0.82</td><td>31.31 ± 25.92</td><td>0.88</td></tr></table>

数据以均值±标准差、中位数（四分位距）或百分比（%）形式呈现。BMI：身体质量指数（Body Mass Index）；NC：颈围（Neck Circumference）；OSA：阻塞性睡眠呼吸暂停（Obstructive Sleep Apnea）；AHI：呼吸暂停低通气指数（Apnea-Hypopnea Index）；M：男性（Male）；F：女性（Female）。a P值通过训练集与验证集的比较获得。b P值通过训练集与测试集的比较获得。

表2 模型在采用三种AHI阈值（≥5、15及30次/小时）时的性能表现。

<table><tr><td></td><td>Sensitivity</td><td>Specificity</td><td>Accuracy</td><td>AUC (95% CI)</td></tr><tr><td>AHI&gt;=5</td><td></td><td></td><td></td><td></td></tr><tr><td>Photographs</td><td>0.905</td><td>0.941</td><td>0.884</td><td>0.881(0.839- 0.922)</td></tr><tr><td>Photographs and clinical variables</td><td>0.875</td><td>0.967</td><td>0.901</td><td>0.900(0.841- 0.944)</td></tr><tr><td>AHI&gt;=15 Photographs</td><td>0.600</td><td>0.978</td><td>0.878</td><td>0.872(0.818-</td></tr><tr><td>Photographs and clinical variables</td><td>0.810</td><td>0.953</td><td>0.881</td><td>0.924) 0.889(0.850- 0.928)</td></tr><tr><td>AHI&gt;=30 Photographs</td><td>0.895</td><td>0.943</td><td>0.874</td><td>0.853(0.815-</td></tr><tr><td>Photographs and</td><td></td><td></td><td></td><td>0.904)</td></tr><tr><td>clinical variables</td><td>0.850</td><td>0.953</td><td>0.887</td><td>0.881(0.809- 0.948)</td></tr></table>

AUC，受试者工作特征曲线下面积（Area Under the Receiver Operating Characteristic Curve）；CI，置信区间（Confidence Interval）；AHI，呼吸暂停低通气指数（Apnea-Hypopnea Index）。

# 3.3. 遮挡（Occlusion）结果

我们基于模型进行了遮挡测试，以预测呼吸暂停低通气指数（AHI）阈值为5次/小时的阻塞性睡眠呼吸暂停（OSA）。在遮挡九个颅面部区域后，正面视图的受试者工作特征曲线下面积（AUC）下降最显著的区域为双侧眼部（ΔAUC=0.082），其次是鼻部（ΔAUC=0.061），以及口部与下颌区域（ΔAUC=0.046）。同时，侧面视图的AUC下降最显著的区域为耳前区（ΔAUC=0.113），其次是耳部（ΔAUC=0.074）。不同颅面部区域遮挡后的AUC变化如图3所示。

正面（front）和侧面（profile）视图的平均贡献值分别为0.045和0.054，其中五个区域显示出高于平均贡献值的特征。基于此，我们为每位参与者创建了加权颅面照片，并分析了改变输入特征对模型输出的影响。结果表明，无论是正面还是侧面加权颅面照片，其预测性能均有所提升。当临床变量与加权颅面照片结合使用时，模型展现出最大的曲线下面积（AUC），达到0.953（图4和图5）。

# 3.4. 重要特征的可视化

通过显著性图（saliency maps）可视化展示了患有与未患有阻塞性睡眠呼吸暂停（OSA）参与者的不同面部特征。如图6(a)所示，在对OSA患者进行分类时，模型主要关注中面部、下颌、耳部及颈部区域。而图6(b)显示，在对非OSA个体进行分类时，模型则着重强调口部区域的特征。

# 3.5. 颅面区域与阻塞性睡眠呼吸暂停（OSA）的关系

与O-4个阳性区域组相比，具有不同呼吸暂停严重程度的5-9个阳性区域组$( \mathbf { P } < 0 . 0 5 )$显示出更高的阻塞性睡眠呼吸暂停（OSA）患病率（图7）。随着阳性颅面区域数量的增加，不同严重程度的OSA患病率呈现上升趋势。

# 4. 讨论 (Discussion)

在本研究中，我们基于深度学习模型利用颅面照片实现了阻塞性睡眠呼吸暂停（OSA）的检测。结果显示，当以呼吸暂停低通气指数（AHI）≥5次/小时作为OSA诊断标准时，该模型的最高灵敏度、特异度、准确率及受试者工作特征曲线下面积（AUC）分别达到90.5%、94.1%、88.4%和0.881。此外，在另外两个常用诊断阈值（15次/小时和30次/小时）下，模型对OSA的分类准确率有所下降。这种随AHI阈值升高而性能下降的现象，在另一项采用面部照片线性与测地线测量数据开发预测算法的研究中也有类似报道[15]。这些结果支持了以下观点：不同严重程度的OSA患者具有共同的颅面表型特征。

通过二维或三维摄影分析可识别阻塞性睡眠呼吸暂停（OSA）患者与非患者间的颅面特征差异，且相关测量数据可用于预测OSA。一项研究采用包含下颌长度、面宽、眼宽及颈颏角四项指标的逻辑回归模型，实现了76.1%的参与者正确分类，其受试者工作特征曲线下面积（AUC）达0.82[8]。另一研究通过口咽结构（舌体面积、悬雍垂面积、系带长度及后置距离）的摄影测量建立预测模型，该模型正确分类率达82.7%，在最佳截断点处灵敏度为85.6%、特异度为84.3%，AUC达0.90[16]。

三维摄影技术能更清晰呈现面部形态轮廓，提供精准分析。相较于二维摄影，三维摄影与计算机断层扫描（CT）在颅面线性距离、角度、面积及体积测量方面具有更高一致性；但无论是二维还是三维摄影，其测量值与呼吸暂停低通气指数（AHI）的关联性均较弱[17]。近期两项研究将多种分类器（k近邻算法、极限梯度提升及卷积神经网络）与三维颅面扫描相结合，用于预测AHI值与OSA患病状态，结果显示准确率约为67%、AUC约0.70[18,19]。这表明三维面部摄影虽未显著提升OSA患者识别效能，但可能成为评估颅面特征的临床实用方法。与此同时，二维摄影因其更易获取且成本低廉，在人群普适性方面更具优势。因此，本研究开发了基于二维颅面分析的OSA预测方法。

![](images/b88dd4e2b98167207f4f9c96d31f509da8630ad30f5dd36696e292a24cb68aa8.jpg)  
图3（Fig3）展示了用户案例（UCas）中自监督特征（fids）的自我增强（ese）过程，该过程通过局部（local）用户数据（Usdt）优化了遮挡区域（occluded region）的处理。

![](images/aa18372a9dd2c911e49c9f25314a06d2a74ed7268b56ac5f13d0ad77e2bed912.jpg)  
图4. 区域加权照片（regional weighed photographs）示例。

![](images/fdaea9b6cee323ae20ac01b3bb8f0f1ba43e196ef3725abe8b9e87db32f01379.jpg)  
图5展示了仅使用加权照片（weighted photographs）以及同时使用加权照片和临床变量（clinical variables）的模型结果对比。

本研究结果显示，双侧眼、鼻、口与颏部、耳部及耳前区域对模型的贡献度高于其他颅面区域。重要区域主要集中在中面部与前部面区。然而，当相应区域的权重增加时，模型性能得到提升，这表明这些区域存在与阻塞性睡眠呼吸暂停（OSA）相关的风险因素。该结果与临床医生观察到的OSA患者经典影像学测量特征以及既往影像学研究结论一致。例如，与非OSA患者相比，OSA患者的眼距和鼻宽更大、颌部更短且后缩、面部更宽。值得注意的是，在存在高龄、肥胖、男性等临床风险因素的情况下，某些测量指标可能对OSA具有保护作用[20,21]。采用CT扫描评估颅面结构的研究表明，鼻宽、颌骨复位角度及额颌缝距离与呼吸暂停低通气指数（AHI）相关，而磨牙间距和后鼻棘至舌骨距离则与上气道塌陷性存在关联[22,23]。

![](images/101cb908ffdb68ce495a13b6a8772e39e6fad8cbcfa7e40a47b45a79b5bbc7d4.jpg)  
图6. (a) 真实平均准确率（Teaeragealiecy）与最高预测概率（thegestpredictedprbbilis）的关系。(b) 真实平均准确率（Teaveragsaliey）与加权预测概率（apsittewespredictedprobi）的关系。

![](images/9581126ba46ec8eb4c38b4205b68e27134c1b7e53b567509010cfb8664070639.jpg)  
图7. 阳性区域数量与阻塞性睡眠呼吸暂停（OSA）患病率的关系。

这些重要测量值被纳入使用深度学习技术识别的区域中。摄影特征的视觉呈现与咬合测试相似，表明阻塞性睡眠呼吸暂停（OSA）患者可能在颅底、上颌骨和下颌骨区域表现出异常的颅面复合体结构。基于深度学习的模型应能从高亮区域揭示与OSA相关的重要风险因素。与正面视图相比，侧面视图可能在颈部区域提供额外的有价值信息。我们推测侧面视图不仅能反映颈部尺寸，还能体现颈部与下颌骨之间的位置关系。咬合测试和可视化显示图均表明耳朵是潜在的风险区域，尽管目前鲜有研究探讨该区域与OSA的关联。我们的模型可能已学习到某些与OSA相关但超出人类感知或理解范围的特征。此外，我们发现了对OSA检测具有意义的阳性颅面区域数量与OSA患病率之间的关联性。个体显示的阳性区域越多，罹患OSA的风险越高。综合来看，这些测试解释了基于深度学习的模型的科学基础与可靠性。

应用颅面照片的另一方法是定义疾病表型并研究与阻塞性睡眠呼吸暂停（OSA）发病机制相关的解剖结构失调。Sutherland等人通过研究证实，面部表面尺寸（通过照片或磁共振成像测量），如面中宽度和下面部高度，能够反映上气道结构的大小[24,25]。尽管本研究采用深度学习技术识别与OSA相关的风险区域，但该方法尚无法精细区分骨骼结构、软组织及局部脂肪组织，因而未能真正评估OSA患者的解剖结构失衡问题。未来需开展更多研究，以分析颅面照片中隐藏的代表性特征与上气道结构（或其他生理特征如咽部临界压、咽部开放压及环路增益）之间的关联。除解剖风险因素外，OSA患者可能存在睡眠面容或吸引力较低的面部特征。深度学习算法能否提取可区分面部外观变化的特异性特征，仍需进一步探究。

# 5．结论 (Conclusion)

基于深度学习（deep learning）的颅面影像分析（craniofacial photographic analysis）有望在门诊实现自动、快速的阻塞性睡眠呼吸暂停（OSA）风险分层（risk stratification），或可作为OSA筛查工具。基于深度学习的高风险决策（high-stakes decision-making）与医学实践紧密交织，我们的研究结果表明，所提出的模型成功捕捉到了与OSA相关的颅面特征（OSA-associated craniofacial features）。

# 资金（Funding）

本研究未从公共、商业或非营利部门的资助机构获得任何特定拨款。

# CRediT 作者贡献声明

帅何：概念化（Conceptualization）、方法论（Methodology）、数据收集（Data collection）、统计分析（Statistical analysis）、撰写初稿（Writing - original draft）。  
李英杰：概念化（Conceptualization）、软件（Software）、技术开发与支持（Technical development and support）、撰写初稿（Writing - original draft）。  
张冲：软件（Software）、技术开发与支持（Technical development and support）。  
李祖飞：概念化（Conceptualization）、临床支持（Clinical support）。  
任媛媛：概念化（Conceptualization）、临床支持（Clinical support）。  
李天成：概念化（Conceptualization）、设计（Design）、方法论（Methodology）、撰写-审阅与编辑（Writing - review & editing）。  
王建廷：概念化（Conceptualization）、设计（Design）、方法论（Methodology）、撰写-审阅与编辑（Writing - review & editing）。

# 利益冲突声明 (Declaration of competing interest)

作者声明，对于本论文所报告的研究工作，不存在任何已知的可能影响研究结果的竞争性经济利益或个人关系（competing financial interests or personal relationships）。

# 致谢

作者谨此感谢所有参与者及同事对本研究给予的支持。

# 附录A. 补充数据 (Supplementary data)

本文的补充数据可在 https://doi.org/10.1016/j.sleep.2023.09.025 在线获取。

# 参考文献 (References)

[1] Benjafield AV, Ayas NT, Eastwood PR, Heinzer R, Ip MSM, Morrell MJ, Nunez CM, Patel SR, Penzel T, Pepin JL, Peppard PE, Sinha S, Tifik S, Valentine K, Malhotra A. 阻塞性睡眠呼吸暂停（Obstructive Sleep Apnoea, OSA）全球患病率及疾病负担的估算：一项基于文献的分析。 Lancet Respir Med 2019;7:687-98.
[2] Veasey SC, Rosen IM. 成人阻塞性睡眠呼吸暂停（Obstructive Sleep Apnea）。N Engl J Med 2019;380: 1442-9.
[3] Werli KS, Otuyama LJ, Bertolucci PH, Rizzi CF, Guilleminault C, Tufik S, Poyares D. 存在残留性过度嗜睡的阻塞性睡眠呼吸暂停患者的神经认知功能：一项前瞻性对照研究。 Sleep Med 2016;26:6-11.
[4] Dewan NA, Nieto FJ, Somers VK. 间歇性低氧血症与阻塞性睡眠呼吸暂停（OSA）。 Chest 2015; 147:266-74.
[5] Schwab R, Pasirstein M, Pierson R, Mackley A, Hachadoorian R, Arens R, Maislin G, Pack AI. 利用容积磁共振成像（Volumetric Magnetic Resonance Imaging）识别阻塞性睡眠呼吸暂停的上气道解剖风险因素。 Am J Respir Crit Care Med 2003;168:522-30.
[6] Chi L, Comyn FL, Mitra N, Reilly MP, Wan F, Maislin G, Chmiewski L, ThorneFitzGerald MD, Victor UN, Pack AI. 利用三维磁共振成像（Three-Dimensional MRI）识别阻塞性睡眠呼吸暂停的颅面风险因素。 Eur Respir J 2011;38: 348-58.
[7] Schorr F, Kayamori F, Hirata RP, Danzi-Soares NJ, Gebrim EM, Moriya HT, Malhotra A, Lorenzi-Filho G, Genta PR. 不同的颅面特征预测日裔巴西人和白种人男性的上气道塌陷性。 Chest 2016;149:737-46.
[8] Lee RW, Petocz P, Prvan T, Chan AS, Grunstein RR, Cistulli PA. 通过颅面摄影分析预测阻塞性睡眠呼吸暂停。 Sleep 2009;32: 46-52.
[9] Sutherland K, Lee RW, Petocz P, Chan TO, Ng S, Hui DS, Cistulli PA. 颅面表型分析在中国人群中预测阻塞性睡眠呼吸暂停。 Respirology 2016;21:1118-25.
[10] Chen X, Wang X, Zhang K, Fung KM, Thai TC, Moore K, Mannel RS, Liu H, Zheng B, Qiu Y. 深度学习在医学图像分析中的最新进展与临床应用。 Med Image Anal 2022;79:102444.
[11] He S, Su H, Li Y, Xu W, Wang X, Han D. 基于颅面图像的深度学习检测阻塞性睡眠呼吸暂停。 Sleep Breath 2022;26:1885-95.
[12] Berry RB, Budhiraja R, Gottlieb DJ, Gozal D, Iber C, Kapur VK, Marcus CL, Mehra R, Parthasarathy S, Quan SF, Redline S, Strohl KP, Davidson Ward SL, Tangredi MM, 美国睡眠医学学会（American Academy of Sleep Medicine）。睡眠中呼吸事件评分规则：2007年美国睡眠医学学会睡眠及相关事件评分手册的更新。美国睡眠医学学会睡眠呼吸暂停定义工作组的审议结果。 J Clin Sleep Med 2012;8:597-619.
[13] Levin AA, Klimov DD, Nechunaev AA, Prokhorenko LS, Mishchenkov DS, Nosova AG, Astakhov DA, Poduraev YV, Panchenkov DN. 超声视频中实验性OpenCV跟踪算法的评估。 Sci Rep 2023;13: 6765.
[14] Van der Velden BHM, Kuijf HJ, Gilhuijs KGA, Viergever MA. 基于深度学习的医学图像分析中的可解释人工智能（Explainable Artificial Intelligence, XAI）。 Med Image Anal 2022;79:102470.
[15] Eastwood P, Gilani SZ, McArdle N, Hillman D, Walsh J, Maddison K, Goonewardene M, Mian A. 通过三维面部摄影预测睡眠呼吸暂停。 J Clin Sleep Med 2020;16:493-502.
[16] He S, Li Y, Xu W, Kang D, Li H, Wang C, Ding X, Han D. 摄影测量法对阻塞性睡眠呼吸暂停的预测价值。 J Clin Sleep Med 2021;17:193-202.
[17] Lin SW, Sutherland K, Liao YF, Cistulli PA, Chuang LP, Chou YT, Chang CH, Lee C, Li LF, Chen NH. 三维摄影用于评估阻塞性睡眠呼吸暂停的面部轮廓。 Respirology 2018;23:618-25.
[18] Monna F, Ben Messaoud R, Navarro N, Baillieul S, Sanchez L, Loiodice C, Tamisier R, Joyeux-Faure M, Pépin JL. 利用机器学习和几何形态测量学从三维颅面扫描预测阻塞性睡眠呼吸暂停。 Sleep Med 2022;95:76-83.
[19] Hanif U, Leary E, Schneider L, Paulsen R, Morse AM, Blackman A, Schweitzer P, Kushida CA, Liu S, Jennum P, Sorensen H, Mignot E. 利用深度学习对三维颅面扫描估计呼吸暂停低通气指数（Apnea-Hypopnea Index）。 IEEE J Biomed Health Inform 2021;25:4185-94.
[20] Lee RW, Chan AS, Grunstein RR, Cistuli PA. 阻塞性睡眠呼吸暂停中的颅面表型分析——一种新颖的定量摄影方法。 Sleep 2009; 32:37-45.
[21] Rizzatti FG, Mazzotti DR, Mindel J, Maislin G, Keenan BT, Bittencourt L, Chen NH, Cistulli PA, McArdle N, Pack FM, Singh B, Sutherland K, Benediktsdottir B, Fietze I, Gislason T, Lim DC, Penzel T, Sanner B, Han F, Li QY, Schwab R, Tufik S, Pack AI, Magalang UJ. 定义国际睡眠中心间阻塞性睡眠呼吸暂停的极端表型。 Chest 2020;158:1187-97.
[22] Gurgel M, Cevidanes L, Pereira R, Costa F, Ruellas A, Bianchi J, Cunali P, Bittencourt L, Junior CC. 与阻塞性睡眠呼吸暂停严重程度及治疗结果相关的三维颅面特征。 Clin Oral Invest 2022;26:875-87.
[23] Thuler E, Seay EG, Woo J, Lee J, Jafari N, Keenan BT, Dedhia RC, Schwartz AR. 上颌横向发育不足预测药物诱导睡眠内镜检查期间上气道塌陷性增加。 Otolaryngol Head Neck Surg 2023;7:258.
[24] Sutherland K, Schwab RJ, Maislin G, Lee RW, Benedikstdsotir B, Pack AI, Gislason T, Juliusson S, Cistuli PA. 定量摄影的面部表型分析反映了冰岛睡眠呼吸暂停患者磁共振成像测量的颅面形态。 Sleep 2014;37:959-68.
[25] Lee RW, Sutherland K, Chan AS, Zeng B, Grunstein RR, Darendeliler MA, Schwab RJ, Cistulli PA. 阻塞性睡眠呼吸暂停患者面部表面尺寸与上气道结构之间的关系。 Sleep 2010;33:1249-54.