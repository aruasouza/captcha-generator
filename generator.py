import numpy as np
from PIL import Image, ImageDraw, ImageFont
import warnings
import os
import random
from scipy.ndimage import zoom
import cv2

warnings.filterwarnings("ignore", category=DeprecationWarning)

fontes_dir = 'fontes'
letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

font_size = 72
canvas_shape = (60,200,3)
border_sides = 5
border_topdown = 15
space = 10
min_radius,max_radius = 5,100
min_proportion = 30

fonte_files = os.listdir(fontes_dir)
image_size = (font_size * 2, font_size * 2)
xlim = (border_sides,canvas_shape[1] - border_sides)
ylim = (border_topdown,canvas_shape[0] - border_topdown)
range_x = xlim[1] - xlim[0]
range_y = ylim[1] - ylim[0]

fontes = [ImageFont.truetype(os.path.join(fontes_dir,font_file), font_size) for font_file in fonte_files]

def generate_canvas():
    return np.ones(canvas_shape) * 255

def linear(x,a,b):
    return x * a + b

def generate_gradient():
    shape = canvas_shape
    canvas = np.array([[[i,i,i] for i in range(shape[1])]] * shape[0])
    inicial_color = [random.randint(0,255) for _ in range(3)]
    final_color = [random.randint(0,255) for _ in range(3)]
    x1,x2 = 0,shape[1]
    a = np.array([(final_color[i] - inicial_color[i]) / (x2 - x1) for i in range(3)])
    b = np.array(inicial_color)
    for i in range(x2):
        canvas[:,i] = (canvas[:,i] * a) + b
    return canvas

def add_noise(canvas):
    for _ in range(2):
        start = (0,random.randint(0,canvas.shape[0] - 1))
        end = (canvas.shape[1] - 1,random.randint(0,canvas.shape[0] - 1))
        color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        canvas = cv2.line(canvas, start, end, color, 1)
    center = (random.randint(0,canvas.shape[1] - 1),random.randint(0,canvas.shape[0] - 1))
    axes = (random.randint(min_radius,max_radius),random.randint(min_radius,max_radius // 2))
    color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    start = random.randint(0,360)
    end = int(start + 360 * (random.randint(50,99) / 100))
    canvas = cv2.ellipse(canvas,center,axes,0,start,end,color,thickness = 1)
    return canvas

def get_letter_image(letter,font):
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)
    text_width, text_height = draw.textsize(letter, font)
    x = (image_size[0] - text_width) / 2
    y = (image_size[1] - text_height) / 2
    draw.text((x, y), letter, font=font, fill="black")
    array = np.array(image)[:,:,0].astype(float)
    array = - (array / 255) + 1
    return array

def resize_img(img,proportion):
    resized = zoom(img,(proportion,proportion),order = 3)
    resized[resized < .5] = 0
    resized[resized > 1] = 1
    return resized

def crop_img(array):
    valid_cols = array.max(axis = 0) > 0
    valid_rows = array.max(axis = 1) > 0
    array = array[valid_rows]
    array = array[:,valid_cols]
    return array

def generate_color(shape):
    color = [random.randint(0,255) for _ in range(3)]
    canvas_color = np.array([[color] * shape[1]] * shape[0]).astype('float64')
    return canvas_color

def print_on_canvas(canvas,letter_img,position):
    height,width = canvas.shape[0],canvas.shape[1]
    big_canvas = np.ones((height * 3,width * 3,3)) * 255
    big_canvas[height:2 * height,width:2 * width] = canvas
    color = generate_color(big_canvas.shape)
    size = random.randint(min_proportion,100) / 100
    resized = resize_img(letter_img,size)
    cropped = crop_img(resized)
    letter_height,letter_width = cropped.shape
    left_bound = round((range_x / 6) * position + border_sides + (space / 2))
    right_bound = round((range_x / 6) * (position + 1) + border_sides - (space / 2))
    top_bound,bottom_bound = ylim
    x,y = random.randint(left_bound,right_bound),random.randint(top_bound,bottom_bound)
    bottom,top = y + (letter_height // 2),y - ((letter_height % 2) + letter_height // 2)
    right,left = x + (letter_width // 2),x - ((letter_width % 2) + letter_width // 2)
    rows_slice = slice(top + height,bottom + height)
    cols_slice = slice(left + width,right + width)
    sl = (rows_slice,cols_slice)
    expanded = cropped[:, :, np.newaxis]
    expanded = np.repeat(expanded, 3, axis=2)
    big_canvas[*sl] = (big_canvas[*sl] * (1 - expanded)) + (color[*sl] * expanded)
    canvas = big_canvas[height:2 * height,width:2 * width]
    left,right,top,bottom = max(left,0),min(right,canvas.shape[1] - 1),max(top,0),min(bottom,canvas.shape[0] - 1)
    x_center,y_center = ((right + left) / 2) / width,((bottom + top) / 2) / height
    w,h = (right - left) / width,(bottom - top) / height
    return canvas,(x_center,y_center,w,h)

def generate_captcha():
    canvas = generate_gradient()
    canvas = add_noise(canvas)
    marks = []
    for i in range(6):
        letter = random.choice(letters)
        font = random.choice(fontes)
        img_letter = get_letter_image(letter,font)
        canvas,coord = print_on_canvas(canvas,img_letter,i)
        marks.append([letter,*coord])
    blur = random.randint(1,4)
    canvas = cv2.blur(canvas,(blur,blur))
    return canvas.astype(int),marks