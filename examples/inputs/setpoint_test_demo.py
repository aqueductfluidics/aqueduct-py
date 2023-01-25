import time

import aqueduct.core.aq
import aqueduct.devices.test_device

params = aqueduct.core.aq.InitParams.parse()
aq = aqueduct.core.aq.Aqueduct(params.user_id, params.ip_address, params.port)
aq.initialize(params.init)

test1: aqueduct.devices.test_device.TestDevice = aq.devices.get("TEST000001")

sf = aq.setpoint(
    name="roc0",
    value=50,
    dtype=int.__name__,
)

sb = aq.setpoint(
    name="roc1",
    value=500,
    dtype=int.__name__,
)

r0 = 50
r1 = 500

while True:
    if sf.value != r0 or sb.value != r1:
        r0 = sf.value
        r1 = sb.value
        test1.set_roc(roc=[r0, r1])
    v1 = test1.get_all_values()
    print(v1)
    time.sleep(.5)
