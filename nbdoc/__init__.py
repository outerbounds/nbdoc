__version__ = "0.0.20"


import sys
_pv = sys.version_info
if _pv < (3, 9):
    raise SystemError(f'nbdoc requires python version 3.9.0 or higher. You are running {_pv.major}.{_pv.minor}.{_pv.micro}')