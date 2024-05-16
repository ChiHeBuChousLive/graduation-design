import cv2
import numpy as np
import matplotlib.pyplot as plt
from . import SVM_ocr




def display(window, img, width, block=False):  # 使用cv2来展示预测结果图片
    """显示图片
    """
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window, width, (int)(width * img.shape[0] / img.shape[1]))
    cv2.imshow(window, img)
    if block:
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def close_op(img, size):
    """形态学闭合操作
    """
    # 创建卷积核
    pre_element = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))  # 返回指定形状和尺寸的结构元素，第一个参数MORPH_RECT表示为矩形，
    # 第二个参数（2,2）表示内核尺寸，第三个参数表示锚点中心位置，默认为（-1，-1），表示锚点位于中心点
    ero_element = cv2.getStructuringElement(cv2.MORPH_RECT,
                                            (size, (int)(size / 8)))
    dil_element = cv2.getStructuringElement(cv2.MORPH_RECT,
                                            (size, (int)(size / 6)))
    # 腐蚀操作
    pre = cv2.erode(img,
                    pre_element,
                    iterations=1)  # 腐蚀操作，理解为图像断开，裂缝变大
    # 膨胀操作
    dil = cv2.dilate(pre,
                     dil_element,
                     iterations=1)  # 膨胀操作，图像断开，裂缝变小
    # 再腐蚀
    ero = cv2.erode(dil,
                    ero_element,
                    iterations=1)  # 腐蚀操作
    return ero


def close_op_y(img, size):
    ero_element = cv2.getStructuringElement(cv2.MORPH_RECT,
                                            ((int)(size / 8), size))
    dil_element = cv2.getStructuringElement(cv2.MORPH_RECT,
                                            ((int)(size / 6), size))
    dil = cv2.dilate(img,
                     dil_element,
                     iterations=1)
    ero = cv2.erode(dil,
                    ero_element,
                    iterations=1)
    return ero


def check_plate(img, rect):
    """检查车牌是否存在
    """
    return True


def draw_rect(img, rect):
    """在图像中绘制矩形区域
    """
    box = cv2.boxPoints(rect)

    return cv2.polylines(img, [box],
                         isClosed=True,
                         color=(0, 0, 255),
                         thickness=1)


# 此函数的设计也有缺陷，改变一下车牌的大小
def scale_rect(rect, scale=1.0):
    """缩放矩形区域
    """
    rect = list(rect)
    scale = scale * rect[1][0] - rect[1][0]
    rect[1] = [x + scale for x in rect[1]]
    return rect


# 重新处理，获得二值图
def getBlueChannel(img):
    """获得图像的绿色和蓝色通道
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([40, 88, 40])
    upper = np.array([124, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    _, s, _ = cv2.split(hsv)
    img = cv2.bitwise_and(s, s, mask=mask)
    display('getBlueChannel', img, 300, block=False)
    return img


# 车牌区域为白色，背景为黑色，调整边界框box，找到每个角点在二值化图像上最接近的白色像素
def adjust_box(img, box):
    """调整车牌区域
    """
    pts = np.array(np.where(img > 0)).T
    pts[:, [0, 1]] = pts[:, [1, 0]]
    new_box = []
    for corner in box:
        new_box.append(list(pts[np.argmin([np.linalg.norm(pt - corner) for pt in pts])]))
    new_box = np.array(new_box)
    new_box[0][0] -= 3
    new_box[3][0] -= 3
    return new_box


# 对于四个点进行排序和标准化，保证左上角为第一个点
def box_normalize(box):
    box = box[np.argsort(box[:, 1])]
    if box[0][0] > box[1][0]:
        box[[0, 1], :] = box[[1, 0], :]
    if box[2][0] < box[3][0]:
        box[[2, 3], :] = box[[3, 2], :]
    return box


def extract_plate(src, rect):
    """从矩形区域中提取车牌
    """
    rect = scale_rect(rect, 1.2)

    """裁剪矩形区域"""
    # 创建一个新的纯黑图
    img = np.zeros_like(src).astype('uint8')
    # 计算四个角的点
    box = np.int0(cv2.boxPoints(rect))
    # 排序四个点
    box = box_normalize(box)
    # 在这个地方填充白色
    img = cv2.fillPoly(img, [box], (255, 255, 255))
    # 这里应该是车牌区域被变成白的了
    cv2.copyTo(src, img, img)

    """图像预处理操作"""
    # 分割通道（？？？？）白色的怎么提取通道？
    img = getBlueChannel(img)
    # 重新预处理
    img = cv2.GaussianBlur(img, (3, 3), 0, 0, cv2.BORDER_DEFAULT)
    th = (np.mean(img) + (np.max(img) - np.mean(img)) * 0.4)
    _, img = cv2.threshold(img, th, 255, cv2.THRESH_BINARY)
    img = close_op(img, 32)

    """调整车牌区域"""
    # 使用红色线条显示图像
    image = cv2.polylines(src, [box], isClosed=True, color=(0, 0, 255), thickness=1)
    # box为所画多边形的顶点坐标，isClosed绘制的图形是否闭合，color:RGB三通道的值，thickness：划线的粗细
    display('image', image, 360, False)
    # 根据白色调整框框大小
    box = adjust_box(img, box)
    # cv2.polylines(src, [box], isClosed=True, color=(0, 0, 255), thickness=1)

    """通过透视变换纠正失真"""
    # 转换为浮点形式，方便透视
    box = box.astype('float32')
    # 将车牌区域映射到一个固定的矩形区域，180*60
    M = cv2.getPerspectiveTransform(box, np.float32([[0, 0], [179, 0], [179, 59], [0, 59]]))  # 构建变换矩阵
    # 透视变换
    plate = cv2.warpPerspective(src, M, (180, 60))  # 透视变换

    return plate


def plot_data(data):
    x = np.linspace(0, len(data), len(data))
    plt.plot(x, data)
    plt.show()


def calc_potential(img):
    """计算势能。
    """
    sum = np.sum(img, 0)  # 计算每一列的和
    pot = np.zeros_like(sum)  # 构造一个和sum一样的零矩阵
    # p为从左往右的势能累计，rp是从右往左
    p, rp = 0, 0
    for i in range(len(sum)):
        """线性增长指数衰减"""
        # 如果当前列的和sum[i]不为0，则增加原数值，否则衰减五分之一
        p = p + sum[i] if sum[i] else p / 5
        # 右边也是一样
        rp = rp + sum[len(sum) - i - 1] if sum[len(sum) - i - 1] else rp / 5
        # p加到pot的当前位置
        pot[i] += p
        # rp加到对称位置
        pot[len(sum) - i - 1] += rp
    # plot_data(pot)
    return pot


def adjust_vision(img):
    """调整视场大小以更好地匹配。
    """
    # display('ch', img, 100, block=True)
    sum = np.sum(img, 1)
    up, down = -1, -1
    for i in range(len(sum)):
        if sum[i] > 512:
            if up == -1:
                up = i
            down = i
    height = down - up + 1
    img = img[up: down + 1, :]
    img = cv2.resize(img, ((int)(img.shape[1] * 1.2), height))
    padding = height - img.shape[1]
    left = (int)(padding / 2)
    right = (int)(padding - left)
    img = np.hstack((np.zeros((height, left)), img))
    img = np.hstack((img, np.zeros((height, right))))
    img = cv2.resize(img, (20, 20))
    return img


def plate_split(img):
    """通过势能拆分字符
    """
    pot = calc_potential(img)  # pot为1*n的矩阵
    limitpot = np.mean(pot) * 0.5  # 对pot取平均值，设置字符分割的阈值
    bound = []  # 建立一个空列表，存放字符位置
    left = 0
    for i in range(len(pot) - 1):
        if pot[i] < limitpot and pot[i + 1] >= limitpot:
            left = i
        elif pot[i] >= limitpot and pot[i + 1] < limitpot:
            bound.append([left, i])
            left = 0
    if left != 0:
        bound.append([left, len(pot - 1)])  # bound为每个车牌字符的具体位置，通过使用数组记录
    return bound


# 这个函数返回的明明是最长的一个字符
def plate_cut_text(img):
    '''
    车牌字符分割，将分割好的车牌区域进行字符分割
    '''
    # 计算所有列的和
    sum = np.sum(img, 1)
    # 设置一个限制
    limit = np.mean(sum) * 0.2
    bound = []
    start = 0
    # 边界点
    for i in range(len(sum) - 1):
        # 边界开始点
        if sum[i] < limit and sum[i + 1] >= limit:
            start = i
        # 边界结束点
        elif sum[i] >= limit and sum[i + 1] < limit:
            bound.append([start, i])
            start = 0
    # 最后一个字符
    if start != 0:
        bound.append([start, len(sum - 1)])
    # 这里好像是想要找出最长的字符区域
    up, down = 0, 0
    for b in bound:
        if b[1] - b[0] > down - up:
            up = b[0]
            down = b[1]

    return img[up: down + 1, :]




def plate_recognition(plate,reader):  # 字符识别代码
    '''
    车牌识别核心代码，使用SVM对分割的车牌字符进行识别，并将识别结果返回
    '''
    # 转换为bgr，bgr更适合
    img = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    th = (np.mean(img) + (np.max(img) - np.mean(img)) * 0.2)
    _, img = cv2.threshold(img, th, 255, cv2.THRESH_BINARY)  # 阈值函数
    img = plate_cut_text(img)
    display('plate th', img, 360)
    bound = plate_split(img)  # 调用plate_split函数，对车牌字符进行拆分，返回一个列表，列表每个值记录车牌每个字符起始位置
    #print('拆分出来的各个字符起始位置：', bound)
    plate_res = []
    for i, b in enumerate(bound):
        display('character_' + str(i), img[:, b[0]:b[1]], 50)
        if b[1] - b[0] > 5 and b[1] - b[0] < 28:  # 判断每个分割出来的字符宽度是否正常
            # 第一张图片，识别中文
            if len(plate_res) == 0:
                ch = reader.recognize_chinese(adjust_vision(img[:, b[0]:b[1] + 1]))[0]  # 识别车牌汉字
            else:
                ch = reader.recognize_alnum(adjust_vision(img[:, b[0]:b[1] + 1]))[0]  # 识别车牌字符
            plate_res.append(ch)  # 将识别结果添加到变量ch中
    return plate_res  # 返回车牌识别结果

#-----------------------------------------------------------------------------------------
def car_discern(car_img):
        reader = SVM_ocr.Reader()

        src=car_img
        """获取绿色蓝色通道"""
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)  # 将RGB图像转换为HSV图像
        h, s, v = cv2.split(hsv)  # 分离H,S,V
        # 蓝色和绿色的区域，正确方法其实是创建两个模板，这里将两个区域集合在一起了
        lower = np.array([100, 90, 40])
        upper = np.array([124, 255, 255])  # 设置阈值
        mask = cv2.inRange(hsv, lower, upper)  # 获取图像蒙版
        # 这里只用了saturation对自己进行模板运算，在ai模型中说最好用v，明度作为灰度图像
        img = cv2.bitwise_and(s, s, mask=mask)  # 在图像蒙版上使用“按位与”运算符吗，分离绿色和蓝色通道
        display('0', img, 360)

        """图像预处理操作"""
        # 直方图均衡化提高精度，
        img = cv2.equalizeHist(img)  # 直方图均衡化，增强对比度：将已知灰度概率密度分布的图像经过变换，使其称为一个均匀灰度概率密度分布的新图像
        # 高斯模糊（为什么能归一化，其实就是在0-255之间）
        img = cv2.GaussianBlur(img, (3, 3), 0, 0, cv2.BORDER_DEFAULT)  # 高斯滤波
        display('1', img, 360)

        """检测图像中的纹理"""
        # 这个的方式也不好，一般来书sobel检测准确度不如canny，而且也不能直接采取取平均值的操作
        flipped = cv2.flip(img, 1)  # 图像翻转，1：水平翻转
        sobel1 = cv2.Sobel(img, cv2.CV_8U, 1, 0, ksize=3)  # 图像边缘检测，Sobel算子，对x轴方向求导
        sobel2 = cv2.flip(cv2.Sobel(flipped, cv2.CV_8U, 1, 0, ksize=3), 1)  # 先平滑图像边缘，再翻转
        img = sobel1 / 2 + sobel2 / 2
        img = img.astype('uint8')  # 强制类型转换
        display('2', img, 360)

        """阈值"""
        #
        th = (np.mean(img) + (np.max(img) - np.mean(img)) * 0.6)
        ret, img = cv2.threshold(img, th, 255, cv2.THRESH_BINARY)  # 简单阈值函数，从灰度图像中获取二进制图像
        display('3', img, 360)

        """形态学闭合操作"""
        img = close_op(img, 36)
        display('4', img, 360)
        # 第一个参数代表只检测最外层的轮廓，
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 检测外形轮廓，返回两个值，第一个值为轮廓本身

        # 过滤轮廓，理论上可以找出多个车牌
        for contour in contours:
            area = cv2.contourArea(contour)  # 计算图像轮廓面积
            if area < 200 or area > 50000:  # 判断车牌轮廓区域
                continue
            # 矩形面积
            rect = cv2.minAreaRect(contour)  # 求出点集contour的最小矩形面积，返回值rec[0]为矩形的中心点，rec[1]为矩形的长和宽，rec[2]矩形的旋转角度
            # 第二个条件用来确保轮廓与其最小矩形面积紧密匹配
            if rect[1][0] * rect[1][1] < 666 or area < rect[1][0] * rect[1][1] * 0.6:
                continue

            dy, dx = contour.flatten().reshape(contour.shape[0], -1).T.ptp(1)
            cwb = rect[1][1] / rect[1][0] if rect[1][1] > rect[1][0] else rect[1][0] / rect[1][1]
            # 宽高比小于2.5或者大于6
            if dy < dx or cwb < 2.5 or cwb > 6:
                continue

            if not check_plate(src, rect):
                continue
            # 这里是重新使用原始图像了
            plate = extract_plate(src, rect)  # src为原始图像，rect为车牌区域坐标
            display('6', plate, 360)  # 这里的plate为提取到的车牌RGB图像，并且对车牌进行了矫正

            plate_res = plate_recognition(plate,reader)  # 调用plate_recognition函数，识别车牌字符，返回结果
            plate_res = ''.join(str(i) for i in plate_res)
            #print('识别结果：', plate_res)
        display('res', src, 720, block=True)
        return plate_res
