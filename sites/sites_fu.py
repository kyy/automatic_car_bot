from logic.constant import FSB, MM, SS
import os.path


def max_min_params(car_input):
    car_input = car_input.split(SS)
    if car_input[4] == FSB:
        car_input[4] = str(MM["MIN_YEAR"])
    if car_input[5] == FSB:
        car_input[5] = str(MM["MAX_YEAR"])
    if car_input[6] == FSB:
        car_input[6] = str(MM["MIN_COST"])
    if car_input[7] == FSB:
        car_input[7] = str(MM["MAX_COST"])
    if car_input[8] == FSB:
        car_input[8] = str(MM["MIN_DIM"] * 1000)
    if car_input[9] == FSB:
        car_input[9] = str(MM["MAX_DIM"] * 1000)
    return car_input


def create_folders():
    if not os.path.exists('logic/database/parse'):
        os.mkdir(os.path.join('logic/database/', 'parse'))
    if not os.path.exists('logic/buffer'):
        os.mkdir(os.path.join('logic/', 'buffer'))
