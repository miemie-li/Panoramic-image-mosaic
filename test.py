import os
import cv2
import imutils
import numpy as np

img_dir = 'images'
names = os.listdir(img_dir)

images = []
for name in names:
    img_path = os.path.join(img_dir, name)
    image = cv2.imread(img_path)
    if image is None:
        print(f"读取图片失败: {name}")
        continue
    print(img_path)
    images.append(image)


def run(output_num):

    stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
    status, stitched = stitcher.stitch(images)

    if status != cv2.Stitcher_OK:
        print(f"不能拼接图片，错误代码 = {status}")
        return

    # 四周填充黑色像素，再得到阈值图
    stitched = cv2.copyMakeBorder(
        stitched, 10, 10, 10, 10, cv2.BORDER_CONSTANT, (0, 0, 0))
    gray = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

    cnts, hierarchy = cv2.findContours(
        thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = max(cnts, key=cv2.contourArea)

    mask = np.zeros(thresh.shape, dtype="uint8")
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

    minRect = mask.copy()
    sub = mask.copy()

    # 开始while循环，直到sub中不再有前景像素
    while cv2.countNonZero(sub) > 0:
        minRect = cv2.erode(minRect, None)
        sub = cv2.subtract(minRect, thresh)

    cnts, hierarchy = cv2.findContours(
        minRect.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = max(cnts, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(cnt)

    # 使用边界框坐标提取最终的全景图
    stitched = stitched[y:y + h, x:x + w]

    cv2.imwrite('outputs/final'+str(output_num)+'.jpg', stitched)


run(2)
