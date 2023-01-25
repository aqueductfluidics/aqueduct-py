import time
import sys
from pathlib import Path

path = Path(__file__).parent.resolve().parent.resolve()
sys.path.extend([str(path)])

import aqueduct.core.aq
import aqueduct.devices.pp.obj
import aqueduct.devices.mfpp.obj
import aqueduct.devices.ohsa.obj

a = aqueduct.core.aq.Aqueduct(1)

a.initialize()

PP_NAME = "MyPP"
MFPP_NAME = "MyMFPP"
OHSA_NAME = "MyOHSA"

a.clear_setup()
a.add_device("PP", PP_NAME)
a.add_device("MFPP", MFPP_NAME)
a.add_device("OHSA", OHSA_NAME)

a.get_setup()

pp: aqueduct.devices.pp.obj.PP = a.devices.get(PP_NAME)
mfpp: aqueduct.devices.mfpp.obj.MFPP = a.devices.get(MFPP_NAME)
ohsa: aqueduct.devices.ohsa.obj.OHSA = a.devices.get(OHSA_NAME)

print(pp, mfpp, ohsa)

a.finish()
