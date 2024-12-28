import base64
import os
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
map_img = {}
#loop all images in current folder
for file in os.listdir('.'):
    if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg'):
        file_name = file.split('.')[0]
        map_img[file_name] = get_img_as_base64(f'{file}')
# Save to json file
import json
with open('img_map.json', 'w') as f:
    json.dump(map_img, f, indent=4)
