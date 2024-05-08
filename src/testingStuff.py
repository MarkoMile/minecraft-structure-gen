import skimage
import torch

arr = [0.9,0.2,0.3]

tensor = torch.FloatTensor(list(map(lambda x: pow(x,1.0/2.2),arr)))

print(tensor)