import torch
# from mcpi.minecraft import Minecraft
import json
import math
from mcrcon import MCRcon
#from rgb2cielab import rgb2cielab
import skimage

def euclidean_distance(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

map_location=torch.device('cpu')

#set these 2 variables to the path of the coords.pt and colors.pt files you want to use
coords = torch.load('./examples/minecraft-steve/coords.pt',map_location=torch.device('cpu'))
colors = torch.load('./examples/minecraft-steve/colors.pt',map_location=torch.device('cpu'))

# CONVERT COLORS TO LAB
cielab_colors = colors
br1 = br2 = br3 = 0
for i in colors:
    br2=br3=0
    for j in i:
        br3=0
        for k in j:
            # # first gamma correction (sRGB -> RGB) [decoding] ------> turns out it is unnecessary
            # cielab_colors[br1][br2][br3]=torch.FloatTensor(list(map(lambda x: pow(x,2.0),cielab_colors[br1][br2][br3])))

            # next convert to cielab (sRGB -> CIE lab)
            cielab_colors[br1][br2][br3]=torch.FloatTensor(skimage.color.rgb2lab(cielab_colors[br1][br2][br3],illuminant="d65"))
            br3+=1
        br2+=1
    br1 +=1

mcblocks = json.load(open('./color_data.json'))

# dictionary of selected blocks to allow
allowedBlocks = json.load(open('./blockDictionary_rgb.json'))

blockDictionary = {}

for item in mcblocks["items"]:
    if(item['is_decoration']==False):
    # FILTERS FOR REMOVING BLOCKS
      if(f"minecraft:{item['texture_name']}" in allowedBlocks):
        blockDictionary["minecraft:"+item['texture_name']] = item['lab']

# CONNECT TO MINECRAFT SERVER
# Set the password and port to the one set in the server.properties file
mcr = MCRcon("127.0.0.1",password='secretpassword',port=42069)
mcr.connect()

# DELETING BIG AREA USED FOR GENERATION

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
    lab = cielab_colors[i[0],i[1],i[2]]
    mcblock = min(blockDictionary, key=lambda key: euclidean_distance(lab, blockDictionary[key]))
    mcr.command(f"setblock {i[1].item()+0} {i[2].item() +5} {i[0].item()+10} {mcblock}")
    placedblocks[mcblock] = placedblocks[mcblock]+1 if mcblock in placedblocks else 1

# # Serializing json
# json_object = json.dumps(blockDictionary, indent=4)
 
# # Writing to sample.json
# with open("blockDictionary_lab.json", "w") as outfile:
#     outfile.write(json_object)

mcr.command("say building mode disabled...")
mcr.disconnect()