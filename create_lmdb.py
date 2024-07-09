from io import BytesIO
import os
import lmdb
from PIL import Image
import numpy as np

# def image_to_nparray(image_path):
#     """将图片文件转换为numpy数组"""
#     with Image.open(image_path) as img:
#         return np.array(img)
def PIL2buf(image):
    """ 将PIL图像转换为字节缓冲 """
    buf = BytesIO()
    image.save(buf, format='png')
    buf.seek(0)
    return buf.read()

def save_images_to_lmdb(source_folder, lmdb_path):
    """将文件夹中的图片保存到LMDB数据库"""
    # 创建或打开LMDB数据库文件
    env = lmdb.open(lmdb_path, map_size=int(1e9))
    idx = 1
    with env.begin(write=True) as txn:
        # 遍历文件夹中的图片文件
        for file_name in os.listdir(source_folder):
            if file_name.endswith('.png'):
                # 提取图片类型（lr或hr）和标签Y
                parts = file_name.split('_')
                image_type = parts[0] + '_' + parts[1]  # 'image_lr' 或 'image_hr'
                label = parts[2].split('.')[0]  # 提取Y
                
                image_path = os.path.join(source_folder, file_name)
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                # image_data = PIL2buf(image_path)
                
                # 键名包含图片类型和索引，例如 'image_lr_0'
                key_name = f"{image_type}-{idx:09d}"
                
                # 将图片数据和标签数据存入数据库
                txn.put(key_name.encode(), image_data)
                txn.put(f"label-{idx:09d}".encode(), label.encode())
                
                idx += 1

        txn.put(f"num-samples".encode(), str(idx-1).encode())
    
    env.close()

# 使用示例
source_folder = '/data/cl/TATT_pcan/select_pic/lr'
lmdb_path = '/data/cl/TATT_pcan/select_pic_lmdb'
save_images_to_lmdb(source_folder, lmdb_path)
