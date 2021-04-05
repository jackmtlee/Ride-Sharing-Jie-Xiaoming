'''
the ride-sharing model. The matching result is a probablity.
'''
import numpy as np
import pandas as pd

from configparser import ConfigParser
import ast

from copy import deepcopy

import gurobipy as grb
from gurobipy import *

import time

from Tools import *
from Entity import *
from DataHelper import *

from datetime import datetime


cp = ConfigParser()
cp.read('para.ini')

NUMBER_OF_DRIVER = int(cp.get('numbers', 'number_of_driver'))

H = 999999

# the starting time and end time for batching window
starting_time = '3/3/2017 18:00'
end_time = '3/3/2017 18:05'


'''load trip record from data set'''
PATH = ''                                                               #  Xiaoming's laptop environment
trip_record_df = pd.read_csv(PATH + 'Jie03.csv')

rider_trip_record_df_by_batch_window = get_trip_record_from_dataframe_by_starting_and_end_time(trip_record_df, starting_time, end_time)

''' the region border of the given trip records'''
get_the_region_border_from_dataframe(rider_trip_record_df_by_batch_window, 'start_location_long')  # -97.667,  -97.748
get_the_region_border_from_dataframe(rider_trip_record_df_by_batch_window, 'start_location_lat')   #  30.472,  30.260
get_the_region_border_from_dataframe(rider_trip_record_df_by_batch_window, 'end_location_long')    #  -97.642,  -97.729
get_the_region_border_from_dataframe(rider_trip_record_df_by_batch_window, 'end_location_lat')     #  30.481,   30.259




# '''# to get driver and rider lists'''
driver_list = Driver.get_driver_list(NUMBER_OF_DRIVER)
rider_list = Rider.get_rider_list(DataHelper.get_rider_record_df_by_timeslot(rider_record_df, time_slot), time_slot,
                                  NUMBER_OF_DRIVER)
# # print('rider list is ', rider_list)
#
NUMBER_OF_RIDER = len(rider_list)
# print('number of rider is ', NUMBER_OF_RIDER)
#

begin = datetime.now()
'''# the following is RO model construction'''
model = grb.Model('dm')
model.setParam('TimeLimit', 60 * 10)
model.Params.MIPFocus = 1
#
# '''# the following are decision variables'''
# x=1 if driver d and rider r are matched, x=0, otherwise (1:1 matching)
x = model.addVars(NUMBER_OF_DRIVER, NUMBER_OF_RIDER, vtype=GRB.BINARY, name='x')
# departure time of rider r
dt = model.addVars(NUMBER_OF_DRIVER, vtype=GRB.CONTINUOUS, name='dt')
#
# the following is obj function

obj_expr = LinExpr()
#
# for d in range(NUMBER_OF_DRIVER):
#     for u in range(2 * (NUMBER_OF_DRIVER + NUMBER_OF_RIDER)):
#         for v in range(2 * (NUMBER_OF_DRIVER + NUMBER_OF_RIDER)):
#             obj_expr.addTerms(nominal_travel_time_matrix_between_points[u][v], x[u, v, d])
#
# # u: rider's origin point id range [2* number_of_driver, 2*number_of_driver + number_of_rider )
# # v: point set that excludes driver's origin
# for d in range(NUMBER_OF_DRIVER):
#     for u in range(2 * NUMBER_OF_DRIVER, 2 * NUMBER_OF_DRIVER + NUMBER_OF_RIDER):
#         for v in range(2 * NUMBER_OF_DRIVER, 2 * (NUMBER_OF_DRIVER + NUMBER_OF_RIDER)):
#             if v != u:
#                 obj_expr.addTerms(-1, x[u, v, d])
#
model.setObjective(obj_expr)
#
'''# the following are constraints'''


# constraint (5) (6)
for d in range(NUMBER_OF_DRIVER):
    for r in range(NUMBER_OF_RIDER):
        rider = rider_list[r]





# constraint (9)
model.addConstrs(x.sum('*', r) <= 1 for r in range(NUMBER_OF_RIDER))
# constraint (10)
model.addConstrs(x.sum(d, '*') <= 1 for d in range(NUMBER_OF_DRIVER))


model.ModelSense = GRB.MAXIMIZE
model.params.LogToConsole = True
model.update()
model.optimize()
#
# model.write('1.lp')
#
# '''the following are values of decision variables'''
#
# print('**************printing routes*****************')
# for v in model.getVars():
#     if v.VarName[:1] == 'x' and v.X == 1.0:
#         print('var {} with value {}'.format(v.VarName, v.X))
#
# print('**************printing matching results*****************')
# # number_of_served_rider = 0
# # for v in model.getVars():
# #     if v.VarName[:1] == 'y' and v.X == 1.0:
# #         i = (v.index - NUMBER_OF_REGION * NUMBER_OF_REGION * NUMBER_OF_DRIVER * NUMBER_OF_RIDER) // NUMBER_OF_RIDER
# #         j = (v.index - NUMBER_OF_REGION * NUMBER_OF_REGION * NUMBER_OF_DRIVER * NUMBER_OF_RIDER) % NUMBER_OF_RIDER
# #         print('driver {} is assigned to rider {}'.format(i, j))
# #         # print('var {} with value {}'.format(v.VarName, v.X))
# #         number_of_served_rider += 1
# # print('obj value is ', z.X)
#
# for v in model.getVars():
#     if v.VarName[:2] == 'dt' and v.X != 0.0:
#         print('var {} with value {}'.format(v.VarName, v.X))

#
end = datetime.now()
print('time elapse.....', end - begin)










