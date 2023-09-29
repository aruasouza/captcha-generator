from generator import generate_captcha
import tempfile
import os
from datetime import datetime
import cv2
import shutil
from pathlib import Path

if __name__ == '__main__':
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
    os.makedirs(images_dir)
    labels_file = os.path.join(path_dir,'labeldata.csv')
    with open(labels_file,'w') as f:
        f.write('id,label,left,right,top,bottom\n')
    i = 0
    while i < n:
        img,marks = generate_captcha()
        name = f'{i}.jpg'
        path = os.path.join(images_dir,name)
        cv2.imwrite(path, img)
        with open(labels_file,'a') as f:
            for mark in marks:
                f.write(f'{i},' + ','.join([str(x) for x in mark]) + '\n')
        i += 1
        progresso = int(100 * i / n)
        print('Progresso:',f'{progresso}%',end = '\r')
    shutil.move(path_dir, downloads)
    print('Finalizado, os arquivos se encontram em',os.path.join(downloads,newdir))
    print('Pressione enter para sair.')
    input()