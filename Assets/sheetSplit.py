from PIL import Image


sheet = Image.open('sheet.png')

width, height = sheet.size

frameW = width / 4
frameH = height / 1
index = 0
for y in range(1):
    for x in range(4):
        area = (x * frameW, y * frameH, x * frameW + frameW, y * frameH + frameH)
        sheet.crop(area).save("Frame{}.png".format(index))
        index += 1
