import xtrack as xt
from pathlib import Path
from subprocess import run, PIPE
from ruamel.yaml import YAML
yaml = YAML(typ='safe')
import time
start = time.time()

from knob_tools import enable_crossing, set_correctors
from error_tools import do_micado
from tfs_tools import store_mb_errors
from tuning_tools import inj_settings_ecloud, tune_line


# Paths
lhcerrors = Path("/eos/project-c/collimation-team/machine_configurations/lhcerrors")
scenarios = Path("/eos/project-c/collimation-team/machine_configurations/LHC_run3/2025/scenarios")


# Load the environment and the configuration
seed = 6
env = xt.Environment.from_json(f'lattices/injection_with_errors_s{seed}.json')
config = yaml.load(scenarios / 'injection.yaml')


# Correction algorithm for MB errors (assigning to spool pieces)
store_mb_errors(env)
file_opt  = Path('temp/optics0_MB.mad')
file_err  = Path('temp/MB.errors')
file_corr = Path('temp/MB_corr_setting.mad')
for linename, _ in env.lines.items():
    if file_opt.exists() or file_opt.is_symlink():
        file_opt.unlink()
    file_opt.symlink_to(f'optics0_MB_{linename}.mad')
    if file_err.exists() or file_err.is_symlink():
        file_err.unlink()
    file_err.symlink_to(f'MB_{linename}.errors')
    cmd = run([f'{lhcerrors}/HL-LHC/corr_MB_ats_v4'], stdout=PIPE, stderr=PIPE)
    if cmd.returncode != 0:
        stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
        raise RuntimeError(f"Correction algorithm failed!\nError given is:\n{stderr}")
    file_corr.rename(f'temp/MB_corr_setting_{linename}.mad')


# call,   file="temp/MB_corr_setting.mad";
# env.vars['on_correction'] = 1


# First micado if needed, then restore the crossing knobs
set_correctors(env)   # TODO: why were they not stored in the json?
do_micado(env)
enable_crossing(env, config)


# Final tuning
for line in env.lines.values():
    env.vars['on_errors'] = 0
    tw_ref = line.twiss()
    env.vars['on_errors'] = 1
    tune_line(line, **inj_settings_ecloud, orbit_ref=tw_ref)
    line.twiss_default.pop("method")


# Store the final environment
env.to_json(f'lattices/injection_with_errors_s{seed}.json')

