import xtrack as xt
import numpy as np
import scipy.constants as sc


def disable_crossing(env, config):
    for knob, _ in config['knob_settings'].items():
        if knob.startswith('on_'):
            env.vars[knob] = 0

def enable_crossing(env, config):
    for knob, val in config['knob_settings'].items():
        if knob.startswith('on_'):
            env.vars[knob] = val


def check_knobs(env, config):
    vart = env.vars.get_table()
    for knob, val in config['knob_settings'].items():
        if knob not in vart.name:
            if knob in ['on_a1', 'on_a5', 'on_o1', 'on_o5']:
                # Unused
                continue
            if knob in ['on_alice_normalized',  'on_lhcb_normalized']:
                env.vars[knob] = 0
                if val > 1:
                    # Sometimes used wrongly
                    env.vars[knob[:-11]] = env.vars[knob]
                else:
                    env.vars[knob[:-11]] = 7000/env.vars['nrj'] * env.vars[knob]
            else:
                print(f"Warning: Knob {knob} not found in the environment.")


def set_cavity_frequency(env, harmonic_number=35640):
    for line in env.lines.values():
        _, cavities = line.get_elements_of_type(xt.Cavity)
        length = line.get_length()
        beta0 = line.particle_ref.beta0[0]
        for name in cavities:
            line[name].frequency = harmonic_number / length * beta0 * sc.c


def add_phase_knob(env):
    # Can use phase_knob, phase_change, phase_knob.b1, phase_change.b1, phase_knob.b2, and phase_change.b2
    env.vars[f'phase_knob'] = 0
    env.vars[f'phase_change'] = env.vars[f'phase_knob']
    env.vars[f'phase_knob.b1'] = env.vars[f'phase_change']
    env.vars[f'phase_change.b1'] = env.vars[f'phase_knob.b1']
    env.vars[f'phase_knob.b2'] = env.vars[f'phase_change']
    env.vars[f'phase_change.b2'] = env.vars[f'phase_knob.b2']
    env.ref['kqtf.a12b1'] -= 0.0022477200000*env.ref['phase_change.b1']
    env.ref['kqtf.a23b1'] -= 0.0006109026670*env.ref['phase_change.b1']
    env.ref['kqtf.a34b1'] -= 0.0006740726670*env.ref['phase_change.b1']
    env.ref['kqtf.a45b1'] += 0.0015222900000*env.ref['phase_change.b1']
    env.ref['kqtf.a56b1'] += 0.0011189300000*env.ref['phase_change.b1']
    env.ref['kqtf.a67b1'] += 0.0020387763940*env.ref['phase_change.b1']
    env.ref['kqtf.a78b1'] -= 0.0011010306070*env.ref['phase_change.b1']
    env.ref['kqtf.a81b1'] -= 0.0001300250000*env.ref['phase_change.b1']
    env.ref['kqtd.a12b1'] -= 0.0001437190000*env.ref['phase_change.b1']
    env.ref['kqtd.a23b1'] += 0.0010619748420*env.ref['phase_change.b1']
    env.ref['kqtd.a34b1'] += 0.0001529048423*env.ref['phase_change.b1']
    env.ref['kqtd.a45b1'] -= 0.0004891330000*env.ref['phase_change.b1']
    env.ref['kqtd.a56b1'] += 0.0008419600000*env.ref['phase_change.b1']
    env.ref['kqtd.a67b1'] += 0.0016072722540*env.ref['phase_change.b1']
    env.ref['kqtd.a78b1'] -= 0.0013696167460*env.ref['phase_change.b1']
    env.ref['kqtd.a81b1'] -= 0.0016425400000*env.ref['phase_change.b1']
    env.ref['kqtf.a12b2'] -= 0.0015000300000*env.ref['phase_change.b2']
    env.ref['kqtf.a23b2'] -= 0.0026080999780*env.ref['phase_change.b2']
    env.ref['kqtf.a34b2'] += 0.0002292920220*env.ref['phase_change.b2']
    env.ref['kqtf.a45b2'] += 0.0018962000000*env.ref['phase_change.b2']
    env.ref['kqtf.a56b2'] += 0.0027266500000*env.ref['phase_change.b2']
    env.ref['kqtf.a67b2'] -= 0.0005254090387*env.ref['phase_change.b2']
    env.ref['kqtf.a78b2'] -= 0.0006960890387*env.ref['phase_change.b2']
    env.ref['kqtf.a81b2']  = 0.0004939700000*env.ref['phase_change.b2']
    env.ref['kqtd.a12b2'] -= 0.0006047010000*env.ref['phase_change.b2']
    env.ref['kqtd.a23b2'] += 0.0007281687569*env.ref['phase_change.b2']
    env.ref['kqtd.a34b2'] += 0.0015548136570*env.ref['phase_change.b2']
    env.ref['kqtd.a45b2'] -= 0.0003441180000*env.ref['phase_change.b2']
    env.ref['kqtd.a56b2'] += 0.0002527790000*env.ref['phase_change.b2']
    env.ref['kqtd.a67b2'] -= 0.0024345517550*env.ref['phase_change.b2']
    env.ref['kqtd.a78b2'] -= 0.0006010707552*env.ref['phase_change.b2']
    env.ref['kqtd.a81b2'] += 0.0014239700000*env.ref['phase_change.b2']


def add_mo_knob(env):
    # Can use i_mo, i_mo.b1, i_oct_b1, i_mo.b2, and i_oct_b2
    env.vars['i_mo'] = 0
    brho = env['nrj'] * 1e9 / sc.c
    for beam in [1, 2]:
        env.vars[f'i_oct_b{beam}'] = env.vars['i_mo']
        env.vars[f'i_mo.b{beam}']  = env.vars[f'i_oct_b{beam}']
        for i in range(1,9):
            env.ref[f'kof.a{i}{i%8+1}b{beam}'] = env.ref['kmax_mo'] * env.ref[f'i_mo.b{beam}'] / env.ref['imax_mo'] / brho
            env.ref[f'kod.a{i}{i%8+1}b{beam}'] = env.ref['kmax_mo'] * env.ref[f'i_mo.b{beam}'] / env.ref['imax_mo'] / brho


def add_tuning_knobs(env, injection=False):
    env.vars['on_sq'] = int(not injection)
    env.vars['kqtf'] = 0
    env.vars['kqtd'] = 0
    env.vars['ksf'] = 0
    env.vars['ksd'] = 0
    env.vars['cmrs'] = 0
    env.vars['cmis'] = 0
    for beam in [1, 2]:
        env.vars[f'dqx.b{beam}'] = (1-env.ref['on_sq']) * env.ref['kqtf']
        env.vars[f'dqy.b{beam}'] = (1-env.ref['on_sq']) * env.ref['kqtd']
        env.vars[f'dqpx.b{beam}'] = (1-env.ref['on_sq']) * env.ref['ksf']
        env.vars[f'dqpy.b{beam}'] = (1-env.ref['on_sq']) * env.ref['ksd']
        env.vars[f'cmrs.b{beam}'] = (1-env.ref['on_sq']) * env.ref['cmrs']
        env.vars[f'cmis.b{beam}'] = (1-env.ref['on_sq']) * env.ref['cmis']
        env.vars[f'dqx.b{beam}_sq'] = env.ref['on_sq'] * env.ref['kqtf']
        env.vars[f'dqy.b{beam}_sq'] = env.ref['on_sq'] * env.ref['kqtd']
        env.vars[f'dqpx.b{beam}_sq'] = env.ref['on_sq'] * env.ref['ksf']
        env.vars[f'dqpy.b{beam}_sq'] = env.ref['on_sq'] * env.ref['ksd']
        env.vars[f'cmrs.b{beam}_sq'] = env.ref['on_sq'] * env.ref['cmrs']
        env.vars[f'cmis.b{beam}_sq'] = env.ref['on_sq'] * env.ref['cmis']


def add_correction_term_to_dipole_correctors(env):
    # Add correction term to all dipole correctors
    env.vars['on_corr_co'] = 1
    for kk in list(env.vars.keys()):
        if kk.startswith('acb'):
            env.vars['corr_co_'+kk] = 0
            env.vars[kk] += (env.vars['corr_co_'+kk] * env.vars['on_corr_co'])


def set_correctors(env):
    crossing_knobs = {'on_a2', 'on_a8', 'on_disp', 'on_o2', 'on_o8', 'on_oh1', 'on_oh2', 'on_oh5', 'on_oh8', 'on_ov1',
                    'on_ov2', 'on_ov5', 'on_ov8', 'on_sep1', 'on_sep2h', 'on_sep2v', 'on_sep5', 'on_sep8h', 'on_sep8v',
                    'on_ssep1', 'on_ssep5', 'on_x1', 'on_x2h', 'on_x2v', 'on_x5', 'on_x8h', 'on_x8v', 'on_xx1', 'on_xx5'}
    crossing_currents = set()
    for nn in env.vars.get_table().name:
        if env.vars[nn]._expr is None:
            continue
        # if nn.startswith('corr_co_'):
        deps = {vv._key for vv in env.vars[nn]._expr._get_dependencies()}
        if any([vvv in crossing_knobs for vvv in deps]):
            crossing_currents.add(nn)
    crossing_correctors = {vvv._key for vv in crossing_currents for vvv in env.vars[vv]._find_dependant_targets()}

    for line in env.lines.values():
        tt = line.get_table()
        mask = ~np.array([nn.startswith('Limit') or nn.startswith('Drift') or nn.startswith('Marker')
                          for nn in tt.element_type])
        tt_h_correctors = tt.rows[mask].rows['mcb.*'].rows['.*h\..*'].name
        line.steering_correctors_x = list({nn for nn in tt_h_correctors if nn not in crossing_correctors})
        tt_v_correctors = tt.rows[mask].rows['mcb.*'].rows['.*v\..*'].name
        line.steering_correctors_y = list({nn for nn in tt_v_correctors if nn not in crossing_correctors})

        tt_monitors = tt.rows[mask].rows['bpm.*'].rows['.*(?<!_entry)$'].rows['.*(?<!_exit)$'].name
        tt_monitors = [nn for nn in tt_monitors if not nn.startswith('bpmwa')]
        tt_monitors = [nn for nn in tt_monitors if not nn.startswith('bpmwb')]
        tt_monitors = [nn for nn in tt_monitors if not nn.startswith('bpmse')]
        tt_monitors = [nn for nn in tt_monitors if not nn.startswith('bpmsd')]
        line.steering_monitors_x = tt_monitors
        line.steering_monitors_y = tt_monitors
