import lmdb
import six
from PIL import Image
from io import BytesIO

def buf2PIL(buf, type='RGB'):
    """ 将字节缓冲转换为PIL图像 """
    stream = BytesIO(buf)
    image = Image.open(stream).convert(type)
    return image

def PIL2buf(image):
    """ 将PIL图像转换为字节缓冲 """
    buf = BytesIO()
    image.save(buf, format='png')
    buf.seek(0)
    return buf.read()

def resize_image(image, scale=0.5):
    """ 对图像进行下采样并恢复到原始尺寸 """
    original_width, original_height = image.size
    new_width, new_height = int(original_width * scale), int(original_height * scale)
    
    # 下采样图像
    resized_image = image.resize((new_width, new_height), Image.BICUBIC)
    
    # 将图像恢复到原始尺寸
    restored_image = resized_image.resize((original_width, original_height), Image.BICUBIC)
    
    return restored_image

# 打开原始LMDB
# env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/SVT', readonly=True)
# env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/IIIT5k', readonly=True)
# env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/IC13_857', readonly=True)
# env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/IC13_1015', readonly=True)
# env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/IC15_1811', readonly=True)
env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/IC15_2077', readonly=True)

# 创建新的LMDB用于存储处理后的图像
# new_env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/IC13_857_resized', map_size=int(1e12))
# new_env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/IC13_1015_resized', map_size=int(1e12))
# new_env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/IC15_1811_resized', map_size=int(1e12))
new_env = lmdb.open('/data/cl/data/benchmark_cleansed/clean_lmdb/IC15_2077_resized', map_size=int(1e12))


with env.begin() as txn, new_env.begin(write=True) as new_txn:
    cursor = txn.cursor()
    count = 0
    for key, value in cursor:
        if b'image' in key:
            # 读取原始图像
            image_hr = buf2PIL(value)
            # 创建下采样图像
            # image_lr = resize_image(image_hr, 0.5)
            image_lr = resize_image(image_hr, 0.25)

            # 保存原始图像和下采样图像
            original_key = key.replace(b'image', b'image_hr')
            new_txn.put(original_key, PIL2buf(image_hr))
            new_key = key.replace(b'image', b'image_lr')
            new_txn.put(new_key, PIL2buf(image_lr))
            print(count)
            count += 1

        if b'label' in key:
            new_txn.put(key, value)
    count = b'%d' %count
    new_txn.put(b'num-samples', count)

# 关闭LMDB环境
env.close()
new_env.close()
