import torch
# from mcpi.minecraft import Minecraft
import json
import math
from mcrcon import MCRcon

def euclidean_distance(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2, _= color2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

map_locaiton=torch.device('cpu')

coords = torch.load('./examples/donut/coords.pt',map_location=torch.device('cpu'))
colors = torch.load('./examples/donut/colors.pt',map_location=torch.device('cpu'))

mcblocks = json.load(open('./average.json'))

blockDictionary = {}

for item in mcblocks['averages']:
    # REMOVING TRANSPARENT BLOCKS, REALLY BLACK BLOCKS (also some weird blocks are 0,0,0,0)
    if(item['pixels'] == 256 
    and item['stddev'] < 40 
    and item['rgba'][3]==0 
    and item['rgba'][0]>10 
    and item['rgba'][1]>10 
    and item['rgba'][2]>10):
    # FILTERS FOR REMOVING BLOCKS
      if(item['image'].find('coral')==-1 
      and item['image'].find('snow')==-1 
      and item['image'].find('trapdoor')==-1 
      and item['image'].find('chorus')==-1 
      and item['image'].find('gravel')==-1 
      and item['image'].find('anvil')==-1 
      and item['image'].find('outside')==-1 
      and item['image'].find('farmland')==-1 
      and item['image'].find('flower')==-1 
      and item['image'].find('inner')==-1 
      and item['image'].find('stalk')==-1 
      and item['image'].find('inside')==-1 
      and item['image'].find('frame')==-1 
      and item['image'].find('_base')==-1 
      and item['image'].find('_top')==-1 
      and item['image'].find('_end')==-1 
      and item['image'].find('_stem')==-1 
      and item['image'].find('sand')==-1 
      and item['image'].find('_powder')==-1 
      and item['image'].find('_top')==-1 
      and item['image'].find('_back')==-1 
      and item['image'].find('_front')==-1 
      and item['image'].find('_stage')==-1 
      and item['image'].find('_side')==-1 
      and item['image'].find('_bottom')==-1):
        blockDictionary["minecraft:"+item['image'][:-4]] = item['rgba']

mcr = MCRcon("127.0.0.1",password='secretpassword',port=42069)
mcr.connect()

# DELETING BIG AREA USED FOR GENERATION
# -13,-60,-9 in minecraft --> -13,-9,-60
# TO
# 131 52 140 in minecraft --> 131 140 52

mcr.command("say deleting mode enabled...")

for i in range(0,5):
    for j in range(0,5):
       for k in range(0,5):
            mcr.command(f'fill {i*30} {j*30} {k*30} {30+i*30} {30+j*30} {30+k*30} air')
            
mcr.command("say deleting mode disabled...")

mcr.command("say building mode enabled...")

placedblocks = {}

for i in coords:
    mcblock = ''
    rgba = colors[i[0],i[1],i[2]]*255
    mcblock = min(blockDictionary, key=lambda key: euclidean_distance(rgba, blockDictionary[key]))
    mcr.command(f"setblock {i[1].item()+0} {i[2].item() +5} {i[0].item()+10} {mcblock}")
    placedblocks[mcblock] = placedblocks[mcblock]+1 if mcblock in placedblocks else 1

# # Serializing json
json_object = json.dumps(blockDictionary, indent=4)
 
# # Writing to sample.json
with open("blockDictionary_rgb.json", "w") as outfile:
    outfile.write(json_object)



mcr.command("say building mode disabled...")
mcr.disconnect()