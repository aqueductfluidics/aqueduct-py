import json

import aqueduct.core.aq

params = aqueduct.core.aq.InitParams.parse()
aq = aqueduct.core.aq.Aqueduct(params.user_id, params.ip_address, params.port)
aq.initialize(params.init)

ipt = aq.input(
    message="Upload a CSV.",
    input_type="csv",
    dtype="str",
)

input_value = json.loads(ipt.get_value())

