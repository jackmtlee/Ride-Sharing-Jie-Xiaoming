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

from datetime import *


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
# get_the_region_border_from_dataframe(rider_trip_record_df_by_batch_window, 'start_location_long')  # -97.667,  -97.748
# get_the_region_border_from_dataframe(rider_trip_record_df_by_batch_window, 'start_location_lat')   #  30.472,  30.260
# get_the_region_border_from_dataframe(rider_trip_record_df_by_batch_window, 'end_location_long')    #  -97.642,  -97.729
# get_the_region_border_from_dataframe(rider_trip_record_df_by_batch_window, 'end_location_lat')     #  30.481,   30.259




# '''# to get driver and rider lists'''
driver_list = Driver.get_driver_list(NUMBER_OF_DRIVER)
rider_list = Rider.get_rider_list(rider_trip_record_df_by_batch_window)

NUMBER_OF_RIDER = len(rider_list)
print('number of rider is ', NUMBER_OF_RIDER)

travel_time_matrix = get_travel_time_matrix_of_driver_origin_and_rider_origin(driver_list, rider_list)
# print(travel_time_matrix)
travel_distance_matrix = get_travel_distance_matrix_of_driver_origin_and_rider_origin(driver_list, rider_list)
# print(travel_distance_matrix)


utility_matrix = get_driver_utility_matrix(driver_list, rider_list)
print(utility_matrix)


begin = datetime.now()
'''# the following is RO model construction'''
model = grb.Model('dm')
model.setParam('TimeLimit', 60 * 10)
model.setParam('NonConvex', 2)
# model.Params.MIPFocus = 1

# '''# the following are decision variables'''
# x=1 if driver d and rider r are matched, x=0, otherwise (1:1 matching)
x = model.addVars(NUMBER_OF_DRIVER, NUMBER_OF_RIDER, obj=utility_matrix, vtype=GRB.BINARY, name='x')
# departure time of rider r
dt = model.addVars(NUMBER_OF_DRIVER, lb = get_converted_rider_time(starting_time), vtype=GRB.CONTINUOUS, name='dt')

# auxiliary variable. z * (dt+t-et+1) = 1, which is an extra constraint
z = model.addVars(NUMBER_OF_DRIVER, vtype=GRB.CONTINUOUS, name='z')

# the following is obj function

obj_expr = QuadExpr()
#obj_expr = LinExpr()
for d in range(NUMBER_OF_DRIVER):
    for r in range(NUMBER_OF_RIDER):
        obj_expr.addTerms(utility_matrix[d][r], x[d, r])
        obj_expr.addTerms(1, z[d], x[d, r])

model.setObjective(obj_expr)


'''# the following are constraints'''


# constraint : z_{i} * (dt_{i} + t_{l(i), o(j)} - et_{j} + 1) = 1
for d in range(NUMBER_OF_DRIVER):
    for r in range(NUMBER_OF_RIDER):
        rider = rider_list[r]
        lhs_constr_expr = QuadExpr()
        lhs_constr_expr.addTerms(1, z[d], dt[d])
        lhs_constr_expr.addTerms(travel_time_matrix[d][r] - get_converted_rider_time(rider.get_rider_earliest_departure_time) + 1, z[d])
        model.addConstr(lhs_constr_expr <= 1)

# constraint (5) (6)
for d in range(NUMBER_OF_DRIVER):
    for r in range(NUMBER_OF_RIDER):
        rider = rider_list[r]
        # model.addConstr(dt[d] + travel_time_matrix[d][r] >= rider.get_rider_earliest_departure_time + H * (x[d, r] - 1))
        model.addConstr(dt[d] + travel_time_matrix[d][r] >= get_converted_rider_time(rider.get_rider_earliest_departure_time) + H * (x[d, r] - 1))  # (5)
        model.addConstr(dt[d] + travel_time_matrix[d][r] <= get_converted_rider_time(rider.get_rider_latest_departure_time) + H * (1 - x[d, r]))    # (6)


# constraint (8)
# model.addConstrs(x.sum('*', r) == x.sum('*', r) for r in range(NUMBER_OF_RIDER))
for r in range(NUMBER_OF_RIDER):
    rider = rider_list[r]
    rider_request_model_type = rider.get_rider_request_model_type
    rhs_expr = LinExpr()
    for d in range(NUMBER_OF_DRIVER):
        driver = driver_list[d]
        driver_model_type = driver.get_driver_model_type
        if driver_model_type == rider_request_model_type:     #  model matched
            rhs_expr.addTerms(1, x[d, r])

    model.addConstr(x.sum('*', r) == rhs_expr)

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

number_of_matched_rider = 0
matched_driver_index_list = []
# the input for the second-stage decision-making model
matched_result_list =[]
for v in model.getVars():
    if v.VarName[:1] == 'x' and v.X == 1.0:
        i = v.index  // NUMBER_OF_RIDER
        j = v.index  % NUMBER_OF_RIDER
        number_of_matched_rider += 1
        matched_driver_index_list.append(i)
        matched_result_list.append(tuple((i, j)))
        print('driver {} with model type {} is assigned to rider {} with model type {}'.format(i, driver_list[i].get_driver_model_type, j, rider_list[j].get_rider_request_model_type))
print('~~~~~~~~~~number of matched rider is ', number_of_matched_rider)


'''print the matched pair'''
for pair in matched_result_list:
    print('driver {} is matched rider {}'.format(pair[0], pair[1]))
# for v in model.getVars():
#     if (v.VarName[:2] == 'dt') and ((v.index - NUMBER_OF_DRIVER*NUMBER_OF_RIDER) in matched_driver_index_list):
#         print('var {} with value {}'.format(v.VarName, v.X))


end = datetime.now()
print('time elapse.....', end - begin)


'''
the following is the second-stage decision, acceptance optimization
'''

model_acc = grb.Model('acc')

# the decision variable for acceptance probality
p = model_acc.addVars(NUMBER_OF_DRIVER, lb=0, ub=1, vtype=GRB.CONTINUOUS, name='p')
# the price that platform gives driver
s = model_acc.addVars(NUMBER_OF_DRIVER, lb=0, vtype=GRB.CONTINUOUS, name='s')
# the auxiliary variable. f*(1-p) = p, exp(s-m) = f
f = model_acc.addVars(NUMBER_OF_DRIVER, lb=0, vtype=GRB.CONTINUOUS, name='f')
# the auxiliary variable.  q = s-m,  exp(q) = f
q = model_acc.addVars(NUMBER_OF_DRIVER, lb=0, vtype=GRB.CONTINUOUS, name='q')
# input is from matched_result_list
obj_expr_2 = QuadExpr()
for i in range(len(matched_result_list)):
    driver_rider_pair = matched_result_list[i]
    print('~~~~~~~~~~', driver_rider_pair)
    rider = rider_list[driver_rider_pair[1]]
    obj_expr_2.addTerms(rider.get_rider_trip_distance, p[i])
    obj_expr_2.addTerms(-1, p[i], s[i])

model_acc.setObjective(obj_expr_2, sense=GRB.MAXIMIZE)
model_acc.setParam('NonConvex', 2)
model_acc.setParam('TimeLimit', 60 * 10)

# model_acc.write('2.lp')

# f*(1-p) = p
model_acc.addConstrs(f[i] - f[i] * p[i] == p[i] for i in range(len(matched_result_list)))

# q = s-m,  exp(q) = f
for i in range(len(matched_result_list)):
    model_acc.addGenConstrExp(q[i], f[i])

# q = s-m
# model_acc.addConstrs(q[i] == s[i] - get_value_4_constraint() for i in range(len(matched_result_list)))
for i in range(len(matched_result_list)):
    value_result = 0
    driver_rider_pair = matched_result_list[i]    #  get matched driver-rider info
    driver_id = driver_rider_pair[0]
    rider_id = driver_rider_pair[1]

    beta_t, beta_d, beta_s, beta_k, beta_c = get_coefficient_4_constraint()

    value_result += beta_c
    value_result += -beta_t * travel_time_matrix[driver_id][rider_id]
    value_result += -beta_d * travel_distance_matrix[driver_id][rider_id]
    value_result += -beta_k * rider_list[rider_id].get_rider_trip_distance

    print('~~~~~~~~~~value result is ', value_result)
    # model_acc.addConstr(q[i] == s[i] - 1)

    model_acc.addConstr(q[i] <= s[i] - value_result)



model_acc.update()
model_acc.optimize()

''''''
for v in model_acc.getVars():
    if v.VarName[:1] == 'p' and v.X != 0.0:
        print('driver {} matched rider {} with probablity {}'.format(matched_result_list[v.index][0], matched_result_list[v.index][1], v.X))
        # print('var {} with value {}'.format(v.VarName, v.X))

'''printing price'''
for v in model_acc.getVars():
    if v.VarName[:1] == 's' and v.X != 0.0:
        print('var name {} with value {} '.format(v.VarName, v.X))
        # print('var {} with value {}'.format(v.VarName, v.X))


