import requant_utils as m
import numpy as np


a = np.array([-99, -2, -1, 0, 1, 2, 3, 2, 3, 4, 2, 1, 99, 99, 7, 7], dtype='int8')
b = np.zeros(a.shape[0]/4, dtype='uint8')

m.requant_8i_2u(a, b)
print a
print b