import xtrack as xt
from pathlib import Path
from subprocess import run, PIPE
from tfs_tools import store_errors


def run_fortran_correction(env, path_errors):
    # Correction algorithm for MB errors (assigning to spool pieces)
    env['on_errors'] = 1
    store_val_on_errors = env['on_errors']
    env['on_correction'] = 1
    store_errors(env, pattern=['mb.*', 'mbh.*'])
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
        cmd = run([(path_errors / "HL-LHC/corr_MB_ats_v4").as_posix()], stdout=PIPE, stderr=PIPE)
        if cmd.returncode != 0:
            stderr = cmd.stderr.decode('UTF-8').strip().split('\n')
            raise RuntimeError(f"Correction algorithm failed!\nError given is:\n{stderr}")
        file_corr.rename(f'temp/MB_corr_setting_{linename}.mad')
    env['on_errors'] = store_val_on_errors


def load_fortran_correction(env):
    env['kqtf.b1'] = env.ref['kqtf']
    env['kqtf.b2'] = env.ref['kqtf']
    env['kqtd.b1'] = env.ref['kqtd']
    env['kqtd.b2'] = env.ref['kqtd']
    env['cmrskew'] = env.ref['cmrs']
    env['cmiskew'] = env.ref['cmis']
    for linename, _ in env.lines.items():
        new_env = xt.Environment()
        new_env.vars.load_madx(f'temp/MB_corr_setting_{linename}.mad')
        vart = new_env.vars.get_table()
        for nn, ex in zip(vart.name, vart.expr):
            if nn in env.vars:
                if nn != 'prad':
                    ex = 0 or ex
                    env.ref[nn] += ex
            else:
                env[nn] = ex
