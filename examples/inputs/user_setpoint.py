import time

from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams

params = InitParams.parse()
aq = Aqueduct(params.user_id, params.ip_address, params.port)
aq.initialize(params.init)

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
    time.sleep(0.1)
    print(sf.value, sb.value)
