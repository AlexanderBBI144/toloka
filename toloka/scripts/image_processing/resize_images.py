from io import BytesIO
import os

from PIL import Image
from tqdm import tqdm


def resize_image(path):
    with open(path, 'rb') as f:
        source_img = Image.open(f)
        filename = path.split('/')[-1]
        source_img.save(path, "JPEG", optimize=True, quality=80)

def resize_all(path):
    for filename in tqdm(os.listdir(path)):
        resize_image(path + filename)

# resize_all('C:/Users/Somov.A/Desktop/Src/')
