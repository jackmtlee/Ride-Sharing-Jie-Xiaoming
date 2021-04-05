from Entity import *
from random import *
import random
from configparser import ConfigParser
import ast
import pandas as pd
import numpy as np
from math import *
import pickle
from Entity import *

cp = ConfigParser()
cp.read('para.ini')



def get_the_region_border_from_dataframe(df, feature):
    print(feature + ' max is {}, min is {}'.format(df[feature].max(), df[feature].min))


def get_distance_by_coordinate(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2  = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2) **2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c*r       # kilometers

def get_distance_between_driver_and_rider(driver, rider):
    pass

def get_distance_matrix_of_driver_and_rider(driver_list, rider_list):
    pass

if __name__ == '__main__':
    pass
    # file = open(r"drivers.bin", "wb")
    # pickle.dump(get_driver_list(300), file)  # 保存list到文件
    # file.close()

