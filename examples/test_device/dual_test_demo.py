import aqueduct.core.aq
import aqueduct.devices.test_device


params = aqueduct.core.aq.InitParams.parse()
aq = aqueduct.core.aq.Aqueduct(params.user_id, params.ip_address, params.port)
aq.initialize(params.init)

test1: aqueduct.devices.test_device.TestDevice = aq.devices.get("test_device_000001")
test2: aqueduct.devices.test_device.TestDevice = aq.devices.get("test_device_000002")

while True:

    for r in range(10, 500, 10):
        test1.set_roc(roc=[int(r), int((250 - r) ** 2)])
        test2.set_roc(roc=[int(r), int((250 - r) ** 2)])
        v1 = test1.get_all_values()
        v2 = test2.get_all_values()
        print(v1, v2)

    for r in range(500, 10, -10):
        test1.set_roc(roc=[int(r), int((250 - r) ** 2)])
        test2.set_roc(roc=[int(r), int((250 - r) ** 2)])
        v1 = test1.get_all_values()
        v2 = test2.get_all_values()
        print(v1, v2)
