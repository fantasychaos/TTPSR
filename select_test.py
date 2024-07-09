import pickle
import lmdb
from PIL import Image
import io
import os

# 目标标签
target_labels = {'fortiflash', 'california', '1996', 'shapes', 'formulas', 'rose', 'obligatorios'}

# LMDB文件路径
# lmdb_path = '/data/cl/TATT_pcan/TextZoom/textzoom/test/easy'
# lmdb_path = '/data/cl/TATT_pcan/TextZoom/textzoom/test/medium'
lmdb_path = '/data/cl/TATT_pcan/TextZoom/textzoom/test/hard'

# 输出文件夹路径
output_folder_hr = 'test_pic/output_images_hr'
output_folder_lr = 'test_pic/output_images_lr'

# 确保输出文件夹存在
os.makedirs(output_folder_hr, exist_ok=True)
os.makedirs(output_folder_lr, exist_ok=True)

# 读取LMDB文件
env = lmdb.open(lmdb_path, readonly=True, lock=False)
with env.begin() as txn:
    cursor = txn.cursor()
    for key, value in cursor:
        # 假设value是包含图片和标签信息的字典
        if b'label' in key:
            # label = value
            label = value.decode('utf-8').lower()
            print(key)
            print(label)
            # 检查标签是否在目标标签中
            if label in target_labels:
                # 获取高分辨率和低分辨率图片
                lr_key = key.replace(b'label', b'image_lr')
                lr_data = txn.get(lr_key)
                hr_key = key.replace(b'label', b'image_hr')
                hr_data = txn.get(hr_key)
                
                image_lr = Image.open(io.BytesIO(lr_data)).convert('RGB')
                image_hr = Image.open(io.BytesIO(hr_data)).convert('RGB')
                
                # 保存图片
                image_hr.save(os.path.join(output_folder_hr, f'{label}_hr_{key.decode("utf-8")}.png'))
                image_lr.save(os.path.join(output_folder_lr, f'{label}_lr_{key.decode("utf-8")}.png'))

print("图片提取完成！")
