import time
import sys
from pathlib import Path

path = Path(__file__).parent.resolve().parent.resolve()
sys.path.extend([str(path)])

import aqueduct.core.aq

a = aqueduct.core.aq.Aqueduct(1)

a.initialize()

p = a.prompt(
    message="testing with pause",
    pause_recipe=True,
)

p = a.prompt(
    message="testing without pause",
    pause_recipe=False,
)

while p:
    print("Waiting...")
    time.sleep(.1)


