from turtle import width
from PIL import Image, ImageDraw
from os import listdir
images = list(filter(lambda x:x[0] in "bw" and x[-3:]=="bmp" and x[-6:-4]!="_t", listdir("media")))
for name in images:
    image = Image.open(f"media/{name}")
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()
    for y in range(height):
        for x in range(width):
            color = pix[x, y]
            avr = sum(color)//3
            if avr >= 127:
                avr = 255
            else:
                avr = 0
            d = (avr, avr, avr)
            if max(color)-min(color)>20:
                d = color
            draw.point((x, y), d)
    image.save(f"media/{name.split('.')[0]}_t.bmp", "BMP")
