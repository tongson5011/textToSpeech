from PIL import Image, ImageDraw, ImageFont
import os
from global_config import *
from global_functions import *

# draw img


def drawIMG(img_start=1, img_counts=1, img_step=4):

    # delete all old img in folders
    if len(os.listdir(imgFolders)) != 0:
        for item in os.listdir(imgFolders):
            os.remove(os.path.join(imgFolders, item))

    if img_counts == 0:
        raise
    img_end = img_start + img_counts * img_step
    fontStyle = 'arial.ttf'
    for img_count in range(img_start, img_end, img_step):
        img_current = img_count + img_step - 1
        img = Image.open(baseIMG)
        img_draw = ImageDraw.Draw(img)
        img_font = ImageFont.truetype(fontStyle, 200)
        img_draw.text(
            (110, 600), f'{img_count} - {img_current}', font=img_font, fill="#000000")
        img.save(f'imgFolders\Chuong{img_count}-{img_current}.png')
        logging.info(
            f'Save image chuong{img_count}-{img_current}.png save success')
        # print(f'{img_count} - {img_current}')


drawIMG(img_start=40, img_counts=5, img_step=4)
