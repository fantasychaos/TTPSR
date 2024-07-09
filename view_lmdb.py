import lmdb
import six
from PIL import Image
from io import BytesIO

# import aspell
# 打开LMDB文件
env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/SVT_resized', readonly=True)
env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/IIIT5k_resized', readonly=True)
# env = lmdb.open('/data/cl/TATT_pcan/TextZoom/textzoom/test/easy', readonly=True)
# env = lmdb.open('/data/cl/TATT_pcan/select_pic_lmdb', readonly=True)


# env = lmdb.open('/data/cl/TPGSR/TextZoom/textzoom/train1', readonly=True)
def buf2PIL(txn, key, type='RGB'):
    imgbuf = txn.get(key)
    buf = six.BytesIO()
    buf.write(imgbuf)
    buf.seek(0)
    im = Image.open(buf).convert(type)
    # im.save("lmdb_visualization.png")     # vis data
    return im

def PIL2buf(image):
    """ 将PIL图像转换为字节缓冲 """
    buf = BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()

def resize_image(image, scale=0.5):
    """ 对图像进行下采样 """
    width, height = image.size
    new_width, new_height = int(width * scale), int(height * scale)
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
    return resized_image

# 开启一个事务
with env.begin() as txn:
    # 获取一个游标
    cursor = txn.cursor()
    index = 0
    count = 0
    hr_count = 0
    lr_count = 0
    
    # s = aspell.Speller('lang', 'en')
    # 遍历所有键值对并打印它们
    for key, value in cursor:
        if b'image_hr' in key:
            if hr_count == 0:
                img = buf2PIL(txn, key, 'RGB')
        #         # img.save('hr_{}.png'.format(index))
                print(img.size)
                hr_count += 1
        if b'image_lr' in key:
            if lr_count == 0:
                img = buf2PIL(txn, key, 'RGB')
        #         img.save('lr_{}.png'.format(index))
                print(img.size)
                lr_count += 1
        #     img.save('lmdb_visualization{}.png'.format(index))
        #     index += 1
        #     if index >= 30:
        #         break
            # continue
        # else:
        # if b'image_hr' in key:
        # print(key)
            # break
        if b'num-samples' in key:
            print(value)
        # print(value)
        
        # if b'label' in key:
        #     # print(key)
        #     if value in s:
        #         count += 1
        #         # print(value)
        #     else:
        #         print(value)
        # # index = index + 1
        
        # if b'num-samples' in key:
        #     print(value)
        #     print(count)
        #     break
        
        
# 关闭LMDB环境
env.close()
