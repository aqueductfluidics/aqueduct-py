"""User Recordable demo."""
from aqueduct.core.aq import Aqueduct
from aqueduct.core.aq import InitParams

params = InitParams.parse()
aq = Aqueduct(params.user_id, params.ip_address, params.port)
aq.initialize(params.init)


v = 1.0

f = aq.recordable(
    name="test_float",
    value=v,
    dtype=float.__name__,
)

increment = aq.setpoint(
    name="increment",
    value=1.0,
    dtype=float.__name__,
)

f.clear()

while True:
    for i in range(0, 100):
        v += increment.value
        f.update(v)
    for i in range(0, 100):
        v -= increment.value
        f.update(v)
