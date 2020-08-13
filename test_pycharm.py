import sys
print(sys.path[0])

import os
print(os.path.abspath('./'))
print(os.path.dirname(__file__))
print(os.getcwd())

from dtnn import dtnn
ss = dtnn
ss.test()