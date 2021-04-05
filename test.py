import pandas as pd
import random

# df = pd.read_csv('Jie03.csv')
# print(df)



# df = pd.read_csv('C:\\Users\\elxxiia\\Desktop\\Ride-Sharing-Jie-Xiaoming\\ride-sharing data\\Jie-Xiaoming-2017.csv')
#
# print(df['requested_car_category'].value_counts())


'''
b'REGULAR'    689869    0
b'SUV'         25346    1
b'PREMIUM'      6357    2
b'LUXURY'       2376    3
'''


# def random_pick(some_list,probabilities):
#     x = random.uniform(0,1)
#     cumulative_probability=0.0
#     for item, item_probability in zip(some_list, probabilities):
#         cumulative_probability+=item_probability
#         if x < cumulative_probability:
#             break
#     return item
#
# driver_model_list = []
# for i in range(20):
#     driver_model_list.append(random_pick([1,2,3,4], [0.1,0.2,0.3,0.4]))
#
# print(driver_model_list)