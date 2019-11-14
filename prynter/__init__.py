from datetime import datetime
import configparser
import os

version = '0.1'
date = datetime.now().strftime('%Y-%m-%d')
dir = os.path.join('output', date)

try:
    os.mkdir('output')
except FileExistsError:
    pass

try:
    os.mkdir(dir)
except FileExistsError:
    pass
    
f_name = input("filename: ")
output_f = os.path.join(dir, date + '-' + f_name)
