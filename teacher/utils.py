import math, random 
import os
from django.core.files.storage import default_storage

# Random รหหัสคอร์สเรียนสำหรับการ join_code   
def generate_class_code(total_digits,existing_codes) :  
    digits = ''.join([str(i) for i in range(0,10)])
    code = ""  
    while True:
        for i in range(total_digits) : 
            code += digits[math.floor(random.random() * 10)] 
        if code not in existing_codes:
            print('Code not in existing codes')
            break
    return code 

# ลบ Path directory ของคอร์สเรียนั้นๆ
import os

def delete_directory(directory_path):
    if not default_storage.exists(directory_path):
        return

    directories, files = default_storage.listdir(directory_path)

    for item in directories:
        item_path = os.path.join(directory_path, item)
        delete_directory(item_path)

    for item in files:
        item_path = os.path.join(directory_path, item)
        if default_storage.exists(item_path):
            default_storage.delete(item_path)

    if default_storage.exists(directory_path):
        default_storage.delete(directory_path)