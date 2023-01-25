import time

import aqueduct.core.aq

a = aqueduct.core.aq.Aqueduct(1, port=49000)

a.initialize()

sf = a.setpoint(
    name="testing_float",
    value=50,
    dtype=float.__name__,
)

sb = a.setpoint(
    name="testing_bool",
    value=True,
    dtype=bool.__name__,
)

while True:
    time.sleep(.1)
    print(sf.value, sb.value)

