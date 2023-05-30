import time

from aqueduct.core.aq import Aqueduct

aq = Aqueduct()
aq.initialize()

aq.initialize()

sf = aq.setpoint(
    name="testing_float",
    value=50,
    dtype=float.__name__,
)

sb = aq.setpoint(
    name="testing_bool",
    value=True,
    dtype=bool.__name__,
)

while True:
    time.sleep(.1)
    print(sf.value, sb.value)

