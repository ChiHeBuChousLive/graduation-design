import os
import cv2
import random
import numpy as np

'''SVM类功能：模型训练、预测'''
class SVM(object):
    def __init__(self, fn):
        self.fn = fn
        if os.path.exists(self.fn): #判断模型是否已经训练过了
            self.model = cv2.ml.SVM_load(self.fn) #如果模型已经存在，则加载训练好的模型
        else:
            self.model = cv2.ml.SVM_create() #否则创建分类器，重新进行训练

    def train(self, samples, responses): #模型训练代码，samples为样本，responses为结果
        self.model.setKernel(cv2.ml.SVM_INTER) #使用线性核
        self.model.train(samples, cv2.ml.ROW_SAMPLE, responses) #对数据进行训练
        self.model.save(self.fn) #保存训练模型

    def predict(self, samples): #模型预测代码，samples为样本
        _, pred = self.model.predict(samples)
        return pred.ravel()

class Reader(object): #读取数据
    def __init__(self) -> None:
        self.svms2 = SVM('static/param/chars2.svm') #读取字符数据
        self.svmsChinese = SVM('static/param/chars2Chinese.svm') #读取汉字数据
        self.groups2 = np.load('static/param/chars2.npy') #读取字符标签
        self.groupsChinese = np.load('static/param/charsChinese.npy') #读取汉字标签


    def recognize_alnum(self, img) -> str: #识别字符
        ret = self.svms2.predict(img.reshape((1, -1)).astype('float32')).astype('int32')
        return self.groups2[ret]

    def recognize_chinese(self, img) -> str: #识别汉字
        ret = self.svmsChinese.predict(img.reshape((1, -1)).astype('float32')).astype('int32')
        return self.groupsChinese[ret]

'''
test函数功能：加载数据集进行训练，输出模型预测精度
'''
def test():
    dataset_root = './dataset' #数据集的根路径
    datasets = ['chars2']  # 数字&字母字符数据集
    # datasets = ['charsChinese'] #这里选择数据集，汉字字符数据集
    data = []
    groups = []
    for dataset in datasets:
        for group in os.listdir(dataset_root + 
                                '/' + dataset):
            for image in os.listdir(dataset_root + 
                                    '/' + dataset + 
                                    '/' + group):
                data.append(np.append(cv2.imread(dataset_root + 
                                                 '/' + dataset + 
                                                 '/' + group + 
                                                 '/' + image, 0).ravel(), len(groups)))
            groups.append(group)

    # np.save('./chars2.npy', np.array(groups))

    random.shuffle(data) #对数据进行混洗
    data = np.array(data).astype('float32') #转换数据格式

    len_train = (int)(data.shape[0] * 0.8) #
    data_train = data[:len_train]
    data_pred = data[len_train:]

    # svm = SVM('./param/chars2Chinese.svm') # 这里创建一个svm模型文件，或者读取一个已有的svm模型文件
    svm = SVM('./param/chars2.svm') # 这里创建一个svm模型文件，或者读取一个已有的svm模型文件
    svm.train(data_train[:, :-1], data_train[:, -1].ravel().astype('int32')) #对svm模型进行训练
    pred = svm.predict(data[:, :-1]) #对训练好的模型进行预测
    print('accuracy: ', np.sum(pred == data[:, -1]) / pred.ravel().shape[0]) #打印模型预测的准确率


if __name__ == '__main__':
    reader = Reader()
    # img = cv2.imread('./dataset/chars2/V/gt_215_2.jpg', 0)
    # txt = reader.recognize_alnum(img)
    img = cv2.imread('./dataset/charsChinese/zh_shan/debug_chineseMat477.jpg', 0)
    txt = reader.recognize_chinese(img)
    print('识别结果为：',txt)

    test() #训练并测试模型的准确率
