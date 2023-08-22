from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.devices.balance import Balance
from aqueduct.devices.base.utils import DeviceTypes
from aqueduct.devices.pump.peristaltic import PeristalticPump

params = InitParams.parse()
aq = Aqueduct(params.user_id, params.ip_address, params.port)
aq.initialize(params.init)

PP_NAME = "MyPP"
OHSA_NAME = "MyOHSA"

aq.clear_setup()
aq.add_device(DeviceTypes.PERISTALTIC_PUMP, PP_NAME, 1)
aq.add_device(DeviceTypes.BALANCE, OHSA_NAME, 4)

aq.get_setup()

pp: PeristalticPump = aq.devices.get(PP_NAME)
ohsa: Balance = aq.devices.get(OHSA_NAME)

print(pp, ohsa)
