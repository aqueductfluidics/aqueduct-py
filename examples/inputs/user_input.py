import time
import sys
from pathlib import Path

path = Path(__file__).parent.resolve().parent.resolve()
sys.path.extend([str(path)])

import aqueduct.core.aq

a = aqueduct.core.aq.Aqueduct(1)

a.initialize()

p = a.input(
    message="testing 1",
    pause_recipe=False,
    dtype=str.__name__,
)

while not p.is_set():
    time.sleep(1)

v = p.get_value()
print(f"Input 1: {v}")

p = a.input(
    message="testing 2",
    pause_recipe=True,
    dtype=str.__name__,
)

v = p.get_value()
print(f"Input 2: {v}")



