import sympy as sy
from sympy import sin, cos, tan
# import numpy as np

th, th_2, th_3, th_4, th_6, th_8, R, L_d, L, L_2 = sy.symbols('th th_2 th_3 th_4 th_6 th_8 R L_d L L_2')
# R_F, R_2, H, th  = sy.symbols('R_F R_2 H th')
# eq_3 = [H - 40, R_F - 58, R_2 - 5]

H = 40
R_F = 58
R_2 = 5


eq = [-th_6 + th + th_4,
      -th_8 + 2 - th_4,
      R * cos(th_3) + R_2 * sin(th_6) - R_F - R_2 * cos(th_8),
      R * sin(th) + R_2 * cos(th_6) - R_2 * sin(th_8)]

eq_2 = [L_d - R_2 * sin(th_4),
        L - H * tan(th),
        L_2 - H * tan(th_2),
        R_F - 2 * H * tan(th_4),
        -R + R_F - 2 * L_d,
        -R_F + L_2 - L]

k = eq+eq_2
print(k)
lm = [th, th_2, th_3, th_4, th_6, th_8, R, L_d, L, L_2]
j = sy.solve(k,*lm)
for i in range(len(j)):
    print(f'{lm[i]} = {j[i]}')
print(j)
