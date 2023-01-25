import json

import aqueduct.core.aq

params = aqueduct.core.aq.InitParams.parse()
aq = aqueduct.core.aq.Aqueduct(params.user_id, params.ip_address, params.port)
aq.initialize(params.init)

log_file_name = dict(
    hint="Enter the desired log file name",
    value="",
    dtype=str.__name__,
    name="log_file_name",
)

polysach_mass = dict(
    hint="Mass of Polysaccharide in milligrams (mg)",
    value=0.0,
    dtype=float.__name__,
    name="polysach_mass",
)

init_cont_g_L = dict(
    hint="Initial concentration target concentration in grams per liter (g/L)",
    value=0.0,
    dtype=float.__name__,
    name="init_cont_g_L",
)

init_product_vol_ml = dict(
    hint="Enter the initial product volume in milliliters (mL)",
    value=0.0,
    dtype=float.__name__,
    name="init_product_vol_ml",
)

initial_transfer_volume = dict(
    hint="Volume to transfer to retentate prior to initial concentration (mL)",
    value=0.0,
    dtype=float.__name__,
    name="initial_transfer_volume",
)

ipt = aq.input(
    message="Enter the requested process parameters.",
    input_type="table",
    dtype="str",
    rows=[
        log_file_name,
        polysach_mass,
        init_cont_g_L,
        init_product_vol_ml,
        initial_transfer_volume,
    ],
)

input_value = json.loads(ipt.get_value())

log_file_name = input_value[0].get("value")
polysach_mass = float(input_value[1].get("value"))
init_cont_g_L = float(input_value[2].get("value"))
init_product_vol_ml = float(input_value[3].get("value"))
initial_transfer_volume = float(input_value[4].get("value"))

print(
    f"""
  log_file_name: {log_file_name},
  polysach_mass: {polysach_mass},
  init_cont_g_L: {init_cont_g_L},
  init_product_vol_ml: {init_product_vol_ml},
  initial_transfer_volume: {initial_transfer_volume}
"""
)
