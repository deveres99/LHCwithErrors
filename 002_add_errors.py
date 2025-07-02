import xtrack as xt
import numpy as np
from pathlib import Path
from ruamel.yaml import YAML
yaml = YAML(typ='safe')
import time
start = time.time()

from knob_tools import disable_crossing, set_correctors
from tfs_tools import store_twiss_reference, read_table
from error_tools import add_error_knobs, veto_for_errors, extend_order_knl_ksl, assign_bend_errors, \
                        assign_quad_errors, assign_sext_errors, assign_skew_sext_errors, \
                        assign_oct_errors, do_micado
from tuning_tools import inj_settings_ecloud, tune_line


# Paths
lhcerrors = Path("/eos/project-c/collimation-team/machine_configurations/lhcerrors")
scenarios = Path("/eos/project-c/collimation-team/machine_configurations/LHC_run3/2025/scenarios")


# Load the environment and the configuration
env = xt.Environment.from_json('lattices/injection_with_apertures.json')
config = yaml.load(scenarios / 'injection.yaml')
seed = 6


# Set knobs and store the reference optics for correction later
disable_crossing(env, config)
add_error_knobs(env)
store_twiss_reference(env)
set_correctors(env)   # TODO: why were they not stored in the json?


# Load the error tables
nrj = 'collision' if env.vars['nrj'] > 2000 else 'injection'
tt_err = read_table(lhcerrors / f'LHC/wise/{nrj}_errors-emfqcs-{seed}.tfs')
tt_rot = read_table(lhcerrors / 'LHC/rotations_Q2_integral.tab')
veto = veto_for_errors(env)


# Errors for the Main Dipoles
print(); print("Assigning errors to Main Dipoles")
extend_order_knl_ksl(env, 'mb.*', order=20)
for nn, vv in tt_err.items():
    if nn.startswith('mb.'):
        assign_bend_errors(env, nn, vv, tt_rot, veto)
do_micado(env)


# Errors for the Separation Dipoles
print(); print(); print("Assigning errors to Separation Dipoles")
for nn, vv in tt_err.items():
    if nn.startswith('mb') and nn[2] != '.':
        assign_bend_errors(env, nn, vv, tt_rot, veto)


# Errors for the Quadrupoles
print(); print(); print("Assigning errors to Quadrupoles")
extend_order_knl_ksl(env, 'mq.*', order=20)
store_val_on_b2s = env['on_b2s']
env['on_b2s'] = 0
for nn, vv in tt_err.items():
    if nn.startswith('mq'):
        assign_quad_errors(env, nn, vv, tt_rot, veto)
env['on_b2s'] = store_val_on_b2s


# # Errors for the Sextupoles and Octupoles
# print(); print(); print("Assigning errors to Sextupoles and Octupoles")
# extend_order_knl_ksl(env, 'ms.*', order=20)
# extend_order_knl_ksl(env, 'mss.*', order=20)
# extend_order_knl_ksl(env, 'mo.*', order=20)
# for nn, vv in tt_err.items():
#     if nn.startswith('ms.'):
#         assign_sext_errors(env, nn, vv, tt_rot, veto)
#     elif nn.startswith('mss.'):
#         assign_skew_sext_errors(env, nn, vv, tt_rot, veto)
#     elif nn.startswith('mo.'):
#         assign_oct_errors(env, nn, vv, tt_rot, veto)
print()


# Store the environment with errors
env.to_json(f'lattices/injection_with_errors_s{seed}.json')

print(f"Error assignments took {time.time() - start:.2f} seconds")
