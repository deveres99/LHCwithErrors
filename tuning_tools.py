import xtrack as xt
import numpy as np


def match_tune_chrom(line, qx, qy, dqx, dqy, tol=1e-3):
    if hasattr(tol, '__iter__'):
        penalty = 1e10
        for this_tol in tol:
            if penalty < this_tol:
                continue
            opt = match_tune_chrom(line, qx=qx, qy=qy, dqx=dqx, dqy=dqy,
                                   tol=this_tol)
            if this_tol != tol[-1]:
                penalty = np.sqrt((opt.target_status(True).residue**2).sum())
        return opt
    return line.match(
        method='6d', # <- passed to twiss
        vary=[
            xt.VaryList(['kqtf', 'kqtd'], step=tol*1e-1, tag='quad'),
            xt.VaryList(['ksf', 'ksd'], step=tol*1e-1, tag='sext'),
        ],
        targets = [
            xt.TargetSet(qx=qx, qy=qy, tol=tol, tag='tune'),
            xt.TargetSet(dqx=dqx, dqy=dqy, tol=tol, tag='chrom'),
        ]
    )


def match_coupling(line, c_minus, tol=1e-3):
    if hasattr(tol, '__iter__'):
        penalty = 1e10
        for this_tol in tol:
            if penalty < this_tol:
                continue
            opt = match_coupling(line, c_minus=c_minus, tol=this_tol)
            if this_tol != tol[-1]:
                penalty = np.sqrt((opt.target_status(True).residue**2).sum())
        return opt
    return line.match(
        method='6d',
        vary=[xt.VaryList(['cmrs', 'cmis'], limits=[-0.5e-2, 0.5e-2], step=tol*1e-1)],
        targets=[
            xt.Target('c_minus_re_0', c_minus, tol=tol), xt.Target('c_minus_im_0', 0, tol=tol)]
    )


def match_tune_chrom_coupling(line, qx, qy, dqx, dqy, c_minus, tol=1e-3):
    if hasattr(tol, '__iter__'):
        penalty = 1e10
        for this_tol in tol:
            if penalty < this_tol:
                continue
            opt = match_tune_chrom_coupling(line, qx=qx, qy=qy, dqx=dqx, dqy=dqy,
                                            c_minus=c_minus, tol=this_tol)
            if this_tol != tol[-1]:
                penalty = np.sqrt((opt.target_status(True).residue**2).sum())
        return opt
    return line.match(
        method='6d', # <- passed to twiss
        vary=[
            xt.VaryList(['kqtf', 'kqtd'], step=tol*1e-1, tag='quad'),
            xt.VaryList(['ksf', 'ksd'], step=tol*1e-1, tag='sext'),
            xt.VaryList(['cmrs', 'cmis'], limits=[-5e-2, 5e-3], step=tol*1e-1, tag='skwew'),
        ],
        targets = [
            xt.TargetSet(qx=qx, qy=qy, tol=tol, tag='tune'),
            xt.TargetSet(dqx=dqx, dqy=dqy, tol=tol, tag='chrom'),
            xt.Target('c_minus_re_0', c_minus, tol=tol),
            xt.Target('c_minus_im_0', 0, tol=tol)
        ]
    )


def tune_line(line, qx, qy, dqx, dqy, c_minus, i_mo=None, phase_knob=None, orbit_ref=None):
    if i_mo:
        line['i_mo'] = i_mo
    if phase_knob:
        line['phase_change'] = int(phase_knob)
    old_twiss_default_method = line.twiss_default.get("method")
    line.twiss_default["method"] = "4d"
    if orbit_ref is not None:
        if line.steering_correctors_x is None or len(line.steering_correctors_x) == 0\
        or line.steering_correctors_y is None or len(line.steering_correctors_y) == 0:
            raise ValueError('No steering correctors found in the line')
        if line.steering_monitors_x is None or len(line.steering_monitors_x) == 0\
        or line.steering_monitors_y is None or len(line.steering_monitors_y) == 0:
            raise ValueError('No steering monitors found in the line')
        if isinstance(orbit_ref, xt.Line):
            orbit_ref = orbit_ref.twiss()
        line.correct_trajectory(twiss_table=orbit_ref)
    match_tune_chrom(line, qx=qx, qy=qy, dqx=dqx, dqy=dqy, tol=[1e-4, 2e-5, 5e-6, 1e-6])
    match_coupling(line, c_minus=c_minus, tol=5e-5)
    match_tune_chrom(line, qx=qx, qy=qy, dqx=dqx, dqy=dqy, tol=[1e-4, 2e-5, 5e-6, 1e-6])
    if old_twiss_default_method:
        line.twiss_default["method"] = old_twiss_default_method


def tune_environment_from_config(env, config, orbit_ref=None):
    for linename, line in env.lines.items():
        this_orbit_ref = orbit_ref[linename] if orbit_ref else None
        tune_line(line, qx=config['qx'][linename], qy=config['qy'][linename],
                  dqx=config['dqx'][linename], dqy=config['dqy'][linename],
                  c_minus=0.001, i_mo=config['knob_settings'][f'i_oct_b{linename[-1]}'],
                  phase_knob=config['knob_settings']['phase_knob'],
                  orbit_ref=this_orbit_ref)
