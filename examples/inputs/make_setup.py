from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams
from aqueduct.devices.balance import Balance
from aqueduct.devices.pump.peristaltic import PeristalticPump

params = InitParams.parse()
aq = Aqueduct(params.user_id, params.ip_address, params.port)
aq.initialize(params.init)

PP_NAME = "MyPP"
OHSA_NAME = "MyOHSA"

aq.clear_setup()
aq.add_device("PP", PP_NAME)
aq.add_device("OHSA", OHSA_NAME)

aq.get_setup()

pp: PeristalticPump = aq.devices.get(PP_NAME)
ohsa: Balance = aq.devices.get(OHSA_NAME)

print(pp, ohsa)
