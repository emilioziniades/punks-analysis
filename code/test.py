import math

from utils import non_equal_intervals

hyperbola = lambda x: 1/(1+x)
square_root = lambda x: x ** (1/2)
cubed_root = lambda x: x ** (1/3)
exponent = lambda x: (math.e ** (x/100)) -1
normal = lambda x: x
log = lambda x: math.log(x + 1)

base_exponent = lambda x, i: i * (math.e ** x) - i
# exponent = lambda x,e: base_exponent(x, e)

# non_equal_intervals(0,10,3, normal)

# non_equal_intervals(10,500,15, normal)

non_equal_intervals(3914495, 12451090,700, exponent)


