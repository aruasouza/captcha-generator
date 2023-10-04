from generator import generate_captcha
import tempfile
import os
from datetime import datetime
import cv2
import shutil
from pathlib import Path
import json

if __name__ == '__main__':
    with open('classes.json','r') as f:
        classes = json.load(f)
        classes = {classes[key]:key for key in classes}
    temp = tempfile.gettempdir()
    downloads = str(Path.home() / "Downloads")
    id = str(datetime.now()).split('.')[0].replace(':','').replace(' ','_')
    newdir = f'captchas_{id}'
    path_dir = os.path.join(temp,newdir)
    print('\n--- Gerador de Captchas para Visão Computacional ---\n')
    while True:
        print('Digite o número de captchas a serem gerados:')
        inp = input().strip()
        try:
            n = int(inp)
            if n < 100000:
                break
            else:
                print('A quantidade máxima é 100.000\n')
        except Exception as e:
            print('Input inválido.\n')
    if os.path.exists(path_dir):
        os.rmdir(path_dir)
    os.makedirs(path_dir)
    images_dir = os.path.join(path_dir,'images')
    labels_dir = os.path.join(path_dir,'labels')
    os.makedirs(images_dir)
    os.makedirs(labels_dir)
    i = 0
    while i < n:
        img,marks = generate_captcha()
        name_img = f'{i}.jpg'
        path_img = os.path.join(images_dir,name_img)
        cv2.imwrite(path_img, img)
        name_txt = f'{i}.txt'
        path_txt = os.path.join(labels_dir,name_txt)
        with open(path_txt,'w') as f:
            for mark in marks:
                classe = classes[mark[0]]
                f.write(f'{classe} ' + ' '.join([str(x) for x in mark[1:]]) + '\n')
        i += 1
        progresso = int(100 * i / n)
        print('Progresso:',f'{progresso}%',end = '\r')
    shutil.move(path_dir, downloads)
    print('Finalizado, os arquivos se encontram em',os.path.join(downloads,newdir))
    print('Pressione enter para sair.')
    input()