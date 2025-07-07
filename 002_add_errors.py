import xtrack as xt
from pathlib import Path
from ruamel.yaml import YAML
yaml = YAML(typ='safe')
import time
start = time.time()

from knob_tools import disable_crossing, enable_crossing
from tfs_tools import store_twiss_reference
from error_tools import add_error_knobs, load_error_table, assign_errors, consider_micado
from tuning_tools import tune_environment_from_config
from correction_tools import run_fortran_correction, load_fortran_correction


seed = 6


# Paths
path_errors = Path("/eos/project-c/collimation-team/machine_configurations/lhcerrors")
path_scenarios = Path("/eos/project-c/collimation-team/machine_configurations/LHC_run3/2025/scenarios")
infile = Path("lattices/injection_clean_with_apertures.json")
outfile = Path(f"lattices/injection_with_errors_s{seed}.json")


# Load the configuration
config = yaml.load(path_scenarios / 'injection.yaml')


# =================================================================================================


# Load the environment
env = xt.Environment.from_json(infile)


# Set knobs and store the reference optics for correction later
disable_crossing(env, config)
add_error_knobs(env)
store_twiss_reference(env)
tw_for_orbit_corr = {linename: line.twiss() for linename, line in env.lines.items()}


# Tune the environment to its nominal settings, such that the relative errors are representative
tune_environment_from_config(env, config)


# Load the error tables
tt_err, tt_rot = load_error_table(env, path_errors, seed, rotation_table=True)

# Errors for the Main Dipoles, Separation Dipoles, and Quadrupoles
assign_errors(env, tt_err, tt_rot, dipoles=True, separation_dipoles=True, quadrupoles=True)

# # Errors for the (Skew) Sextupoles and Octupoles
# # Only fidel tables have errors for these magnets
# tt_err = load_error_table(env, path_errors, seed, table_type='fidel')
# assign_errors(env, tt_err, tt_rot, sextupoles=True, skew_sextupoles=True, octupoles=True)



# Do the correction (for the time being, with the FORTRAN code)
run_fortran_correction(env, path_errors)
load_fortran_correction(env)


# First micado if needed, then restore the crossing knobs
consider_micado(env)
enable_crossing(env, config)


# Final tuning
tune_environment_from_config(env, config, tw_for_orbit_corr)
for line in env.lines. values():
    line.twiss_default.pop("method", None)


# Store the environment with errors
env.to_json(outfile)
print(f"Error assignments took {time.time() - start:.2f} seconds")
