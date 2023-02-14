import numpy as np


abw = np.load('abw_models.npy', allow_pickle=True).item()
av = np.load('av_models.npy', allow_pickle=True).item()
onliner = np.load('onliner_models.npy', allow_pickle=True).item()

print(f'onliner: {len(onliner)}\n'
      f'abw: {len(abw)}\n'
      f'av: {len(av)}')

print(f"{sorted(abw['Audi'])}\n{sorted(av['Audi'])}\n{sorted(onliner['Audi'])}")



if __name__ == '__main__':
    pass