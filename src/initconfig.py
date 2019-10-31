from datetime import datetime
import configparser
import os

version = '0.1'
date = datetime.now().strftime('%Y-%m-%d')
dir = os.path.join('output', date)
try:
    os.mkdir(dir)
except FileExistsError:
    pass

with open('assets/header.gcode', 'r') as f:
    header = f.readlines()
header = "".join(header)

with open('assets/footer.gcode', 'r') as f:
    footer = f.readlines()
footer = "".join(footer)

with open('assets/splash.txt', 'r') as f:
    splash = f.readlines()
splash = "".join(splash)

with open('assets/config.txt', 'r') as f:
    cfgtxt = f.readlines()
cfgtxt = "".join(cfgtxt)


config = configparser.ConfigParser()
config.read('config.ini')

gap = float(config['DEFAULT']['gap'])
width = float(config['DEFAULT']['width'])
height = float(config['DEFAULT']['height'])
filament_diameter = float(config['DEFAULT']['filament_diameter'])
bed_x = float(config['DEFAULT']['bed_x'])
bed_y = float(config['DEFAULT']['bed_y'])
bed = [bed_x, bed_y]
vel = float(config['DEFAULT']['vel'])

print(splash.format(version, gap, width, height, filament_diameter, bed_x, bed_y))
f_name = input("filename: ")

output_f = os.path.join(dir, date + '-' + f_name)
print(output_f)

with open(output_f + '-config.txt', 'w') as f:
    f.write(cfgtxt.format(version, date + '-' + f_name, gap, width, height, vel, filament_diameter, bed_x, bed_y))
