import os
import runpy
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
for name in (".", _dir):
    if name not in sys.path:
        sys.path.insert(0, name)
runpy.run_path(os.path.join(_dir, os.path.basename(__file__)[:-4] + ".py"), run_name="__main__")