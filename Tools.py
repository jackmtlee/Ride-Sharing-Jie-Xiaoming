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

from datetime import *

cp = ConfigParser()
cp.read('para.ini')

gamma = int(cp.get('speed', 'gamma'))

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

def get_distance_between_driver_origin_and_rider_origin(driver, rider):
    driver_origin = driver.get_driver_origin
    rider_origin = rider.get_rider_origin
    return get_distance_by_coordinate(driver_origin[0], driver_origin[1], rider_origin[0], rider_origin[1])

'''get the travel time of drivers and riders by the travel distance. time = distance / speed'''
def get_travel_time_matrix_of_driver_origin_and_rider_origin(driver_list, rider_list):
    distance_matrix_of_driver_and_rider = []
    for d in range(len(driver_list)):
        distance_list_of_one_driver_and_riders = []
        driver = driver_list[d]
        # driver_origin = driver.get_driver_origin
        for r in range(len(rider_list)):
            rider = rider_list[r]
            # rider_origin = rider.get_rider_origin
            distance_list_of_one_driver_and_riders.append(get_distance_between_driver_origin_and_rider_origin(driver, rider))
        distance_matrix_of_driver_and_rider.append(distance_list_of_one_driver_and_riders)

    return np.array(distance_matrix_of_driver_and_rider) / gamma     #  convert distance to travel time

'''get travel distance of drivers and riders, quite simlar as the function above'''
def get_travel_distance_matrix_of_driver_origin_and_rider_origin(driver_list, rider_list):
    distance_matrix_of_driver_and_rider = []
    for d in range(len(driver_list)):
        distance_list_of_one_driver_and_riders = []
        driver = driver_list[d]
        # driver_origin = driver.get_driver_origin
        for r in range(len(rider_list)):
            rider = rider_list[r]
            # rider_origin = rider.get_rider_origin
            distance_list_of_one_driver_and_riders.append(get_distance_between_driver_origin_and_rider_origin(driver, rider))
        distance_matrix_of_driver_and_rider.append(distance_list_of_one_driver_and_riders)

    return distance_matrix_of_driver_and_rider



def get_driver_utility_matrix(driver_list, rider_list):
    travel_distance_matrix = get_travel_distance_matrix_of_driver_origin_and_rider_origin(driver_list, rider_list)
    travel_time_matrix = get_travel_time_matrix_of_driver_origin_and_rider_origin(driver_list, rider_list)

    return 1 / (np.array(travel_distance_matrix) * alpha + np.array(travel_time_matrix) * beta)


def get_rider_utility_matrix():
    pass


'''convert the datetime of rider_time to hour, e.g. 8:10 am -> 8.167
using this method, the input time must be a string!!!
'''
def get_converted_rider_time(rider_time):
    rider_time = datetime.strptime(rider_time, '%m/%d/%Y %H:%M')
    return rider_time.hour + rider_time.minute / 60

#  the coefficients for driver utility
# (b - a) * random_sample() + a,  random value ranges in [a, b)
a = 0
b = 1
def get_coefficient_4_constraint():
    beta_t = (5-3) * np.random.random_sample() + 3    #  travel time coeff                 (1,2)
    beta_d = (b-a) * np.random.random_sample() + a    #  distance coeff o(d)-o(r)   (1,2)
    beta_s = (2-a) * np.random.random_sample() + 2   #  price coeff                (1,2)
    beta_k = (b-a) * np.random.random_sample() + a   #  distance coeff o(r)-w(r)   (1,2)
    beta_c = (10-8) * np.random.random_sample() + 8    #  driver refuse to go coeff  (1,2)

    return beta_t, beta_d, beta_s, beta_k, beta_c




if __name__ == '__main__':
    pass
    value = pd.to_datetime('3/3/2017 18:15')
    # value = get_converted_rider_time('3/3/2017 18:15')
    # print(value)
    # file = open(r"drivers.bin", "wb")
    # pickle.dump(get_driver_list(300), file)  # 保存list到文件
    # file.close()

