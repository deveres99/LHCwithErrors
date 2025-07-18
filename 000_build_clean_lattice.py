import xtrack as xt
from pathlib import Path
from ruamel.yaml import YAML
yaml = YAML(typ='safe')
import time
start = time.time()

from knob_tools import set_cavity_frequency, add_phase_knob, add_mo_knob, add_tuning_knobs, check_knobs, \
                       set_correctors
from slice_tools import slice_env
from tuning_tools import tune_line


# Paths
path_acc_models = Path("/eos/project-c/collimation-team/machine_configurations/acc-models/lhc/2025")
path_optics = Path("/afs/cern.ch/eng/lhc/optics/runIII/RunIII_dev")
path_scenarios = Path("/eos/project-c/collimation-team/machine_configurations/LHC_run3/2025/scenarios")
outfile = Path("lattices/injection_clean.json")

# Load the configuration
config = yaml.load(path_scenarios / 'injection.yaml')
settings_clean = {'qx': 62.28,  'qy': 60.31,  'dqx': 0,  'dqy': 0,  'i_mo': 0,   'c_minus': 0}
# settings_clean = {'qx': 62.31,  'qy': 60.32,  'dqx': 0,  'dqy': 0,  'i_mo': 0,   'c_minus': 0}  # After tune-change


# =================================================================================================


# Load the model
env = xt.load_madx_lattice(path_acc_models / "lhc.seq", reverse_lines=['lhcb2'])
env.vars.load_madx(path_optics / config['optics'])
env.vars.default_to_zero = False
for line in env.lines.values():
    line.particle_ref = xt.Particles.reference_from_pdg_id('proton', p0c=config['knob_settings']['nrj']*1e9)
    line.twiss_default["co_search_at"] = "ip7"
    line.twiss_default["method"] = "4d"
    if "b2" in line.name:
        line.twiss_default["reverse"] = True
set_cavity_frequency(env)
add_phase_knob(env)
add_mo_knob(env)
add_tuning_knobs(env, injection=True)
set_correctors(env)
check_knobs(env, config)


# Apply the knob settings for this scneario
for knob, val in config['knob_settings'].items():
    env.vars[knob] = val


# # Slice
# slice_env(env, slicefactor=4)


# Tuning
for line in env.lines.values():
    tune_line(line, **settings_clean)


# Save the environment
env.to_json(outfile)
print(f"Building took {time.time() - start:.2f} seconds")
