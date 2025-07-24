import numpy as np
import re
from collections import defaultdict
from math import factorial
from tfs_tools import read_table

_MAX_ORDER = 15  # Maximum order of errors to be assigned


def add_error_knobs(env):
    if 'on_errors' not in env.vars: env['on_errors'] = 1
    for i in range(1, 3):
        if f'on_a{i}s' not in env.vars: env[f'on_a{i}s'] = 0
        if f'on_a{i}r' not in env.vars: env[f'on_a{i}r'] = 0
        if f'on_b{i}s' not in env.vars: env[f'on_b{i}s'] = 0
        if f'on_b{i}r' not in env.vars: env[f'on_b{i}r'] = 0
    for i in range(3, _MAX_ORDER+1):
        if f'on_a{i}s' not in env.vars: env[f'on_a{i}s'] = 1
        if f'on_a{i}r' not in env.vars: env[f'on_a{i}r'] = 1
        if f'on_b{i}s' not in env.vars: env[f'on_b{i}s'] = 1
        if f'on_b{i}r' not in env.vars: env[f'on_b{i}r'] = 1


def load_error_table(env, path, seed, table_type='wise', rotation_table=False):
    if table_type not in ['wise', 'fidel']:
        raise ValueError(f"Invalid table_type: {table_type}. Choose 'wise' or 'fidel'.")
    nrj = 'collision' if env['nrj'] > 2000 else 'injection'
    tt_err = read_table(path / f'LHC/{table_type}/{nrj}_errors-emfqcs-{seed}.tfs')
    if rotation_table:
        tt_rot = read_table(path / 'LHC/rotations_Q2_integral.tab')
        return tt_err, tt_rot
    else:
        return tt_err


def assign_errors_single_magnet(env, name, error_list, order, kl_ref, is_skew=False,
                                is_rotated=False, is_beam4=False, magnetic_sign=True,
                                Rr=0.017):
    # Check if there is a sign flip needed:
    yfac = 1
    if magnetic_sign:
        # Magnet designers work with left-handed coordinates
        yfac *= -1
    if is_beam4:
        yfac *= -1
    if is_rotated:
        yfac *= -1
    # In case of a sign flip, the main field changes sign as well if skew and
    # even order or if regular and odd order (order as from KL, not A/B).
    # Example: A1, B2, A3, B4, ...
    if yfac < 0:  # Sign flip
        sign = (-1)**order
        if is_skew:
            sign *= -1
        kl_ref *= sign
    bn_s = [error_list[f'b{i}']*yfac if i%2==0 else error_list[f'b{i}']
            for i in range(1, _MAX_ORDER+1) if f'b{i}' in error_list]
    an_s = [error_list[f'a{i}']*yfac if i%2==1 else error_list[f'a{i}']
            for i in range(1, _MAX_ORDER+1) if f'a{i}' in error_list]
    for i, bn in enumerate(bn_s):
        env[name].knl[i] += bn * env.vars['on_errors'] * env.vars[f'on_b{i+1}s'] * \
                            kl_ref * (Rr**(order-i)) * factorial(i) / factorial(order)
    for i, an in enumerate(an_s):
        env[name].ksl[i] += an * env.vars['on_errors'] * env.vars[f'on_a{i+1}s'] * \
                            kl_ref * (Rr**(order-i)) * factorial(i) / factorial(order)

def assign_errors(env, error_table, rotation_table, dipoles=False, separation_dipoles=False,
                  quadrupoles=False, sextupoles=False, skew_sextupoles=False, octupoles=False,
                  corrector_dipoles=False, corrector_sextupoles=False, corrector_skew_sextupoles=False,
                  corrector_octupoles=False, corrector_skew_octupoles=False, corrector_decapoles=False,
                  corrector_dodecapoles=False):
    # Some magnets are unplugged from the lattice (put as Drifts), so we veto them
    veto = _veto_for_errors(env)

    # First do the main dipoles, and a micado if k0 errors are assigned
    if dipoles:
        _extend_order_knl_ksl(env, 'mb\..*')
        for nn, err in error_table.items():
            if nn.startswith('mb.'):
                name, beam, magnets = _get_name_from_slot(nn, err, env)
                is_rotated = _is_rotated(name, rotation_table)
                for this_name in magnets:
                    if this_name in veto:
                        continue
                    if this_name not in env.elements:
                        print(f"Warning: {this_name} not found in environment, not assigning errors.")
                        continue
                    ee = env[this_name]
                    eeref = env.ref[this_name]
                    kref = eeref.k0 if hasattr(ee, 'k0') else eeref.knl[0]
                    assign_errors_single_magnet(env, this_name, err, order=0, is_skew=False,
                                                kl_ref=1e-4 * kref * env[this_name].length,
                                                is_rotated=is_rotated, is_beam4=(beam==2), Rr=0.017)
        consider_micado(env)

    # Now all the other magnets
    startswith = []
    if separation_dipoles:
        _extend_order_knl_ksl(env, 'mb[^.].*')
        startswith += ['mb']
    if quadrupoles:
        _extend_order_knl_ksl(env, 'mq\..*')
        startswith += ['mq.']
    if sextupoles:
        _extend_order_knl_ksl(env, 'ms\..*')
        startswith += ['ms.']
    if skew_sextupoles:
        _extend_order_knl_ksl(env, 'mss\..*')
        startswith += ['mss.']
    if octupoles:
        _extend_order_knl_ksl(env, 'mo\..*')
        startswith += ['mo.']
    if corrector_dipoles:
        _extend_order_knl_ksl(env, 'mcb.*')
        startswith += ['mcb.']
    if corrector_sextupoles:
        _extend_order_knl_ksl(env, 'mcs\..*')
        _extend_order_knl_ksl(env, 'mcsx\..*')
        startswith += ['mcs.', 'mcsx.']
    if corrector_skew_sextupoles:
        _extend_order_knl_ksl(env, 'mcssx\..*')
        startswith += ['mcssx.']
    if corrector_octupoles:
        _extend_order_knl_ksl(env, 'mco\..*')
        _extend_order_knl_ksl(env, 'mcox\..*')
        startswith += ['mco.', 'mcox.']
    if corrector_skew_octupoles:
        _extend_order_knl_ksl(env, 'mcosx\..*')
        startswith += ['mcosx.']
    if corrector_decapoles:
        _extend_order_knl_ksl(env, 'mcd\..*')
        startswith += ['mcd.']
    if corrector_dodecapoles:
        _extend_order_knl_ksl(env, 'mctx\..*')
        startswith += ['mctx.']
    store_val_on_b2s = env['on_b2s']
    env['on_b2s'] = 0
    for nn, err in error_table.items():
        if any([nn.startswith(start) for start in startswith]):
            if nn.startswith('mb.'):
                # Main Dipole, already handled above
                continue
            name, beam, magnets = _get_name_from_slot(nn, err, env)
            is_rotated = _is_rotated(name, rotation_table)
            for this_name in magnets:
                if this_name in veto: continue
                if this_name not in env.elements:
                    print(f"Warning: {this_name} not found in environment, not assigning errors.")
                    continue
                ee = env[this_name]
                eeref = env.ref[this_name]
                if nn.startswith('mb') or nn.startswith('mcb'):
                    kref = eeref.k0 if hasattr(ee, 'k0') else eeref.knl[0]
                    assign_errors_single_magnet(env, this_name, err, order=0, is_skew=False,
                                                kl_ref=1e-4 * kref * ee.length,
                                                is_rotated=is_rotated, is_beam4=(beam==2), Rr=0.017)
                elif nn.startswith('mq.'):
                    # Quadrupole
                    # These don't seem to follow the magnetic sign convention. Not sure why...
                    kref = eeref.k1 if hasattr(ee, 'k1') else eeref.knl[1]
                    assign_errors_single_magnet(env, this_name, err, order=1, is_skew=False,
                                                kl_ref=1e-4 * kref * ee.length,
                                                is_rotated=is_rotated, is_beam4=(beam==2), Rr=0.017,
                                                magnetic_sign=False)
                elif nn.startswith('ms.') or nn.startswith('mcs.') or nn.startswith('mcsx.'):
                    # Sextupole
                    kref = eeref.k2 if hasattr(ee, 'k2') else eeref.knl[2]
                    assign_errors_single_magnet(env, this_name, err, order=2, is_skew=False,
                                                kl_ref=1e-4 * kref* ee.length,
                                                is_rotated=is_rotated, is_beam4=(beam==2), Rr=0.017)
                elif nn.startswith('mss.') or nn.startswith('mcssx.'):
                    # Skew Sextupole
                    kref = eeref.k2s if hasattr(ee, 'k2s') else eeref.ksl[2]
                    assign_errors_single_magnet(env, this_name, err, order=2, is_skew=True,
                                                kl_ref=1e-4 * kref * ee.length,
                                                is_rotated=is_rotated, is_beam4=(beam==2), Rr=0.017)
                elif nn.startswith('mo.') or nn.startswith('mco.') or nn.startswith('mcox.'):
                    # Octupole
                    kref = eeref.k3 if hasattr(ee, 'k3') else eeref.knl[3]
                    assign_errors_single_magnet(env, this_name, err, order=3, is_skew=False,
                                                kl_ref=1e-4 * kref * ee.length,
                                                is_rotated=is_rotated, is_beam4=(beam==2), Rr=0.017)
                elif nn.startswith('mcosx.'):
                    # Skew Octupole
                    kref = eeref.k3s if hasattr(ee, 'k3s') else eeref.ksl[3]
                    assign_errors_single_magnet(env, this_name, err, order=3, is_skew=True,
                                                kl_ref=1e-4 * kref * ee.length,
                                                is_rotated=is_rotated, is_beam4=(beam==2), Rr=0.017)
                elif nn.startswith('mcd.'):
                    # Decapole
                    kref = eeref.knl[4]
                    assign_errors_single_magnet(env, this_name, err, order=4, is_skew=False,
                                                kl_ref=1e-4 * kref * ee.length,
                                                is_rotated=is_rotated, is_beam4=(beam==2), Rr=0.017)
                elif nn.startswith('mctx.'):
                    # Dodecapole
                    kref = eeref.knl[5]
                    assign_errors_single_magnet(env, this_name, err, order=5, is_skew=False,
                                                kl_ref=1e-4 * kref * ee.length,
                                                is_rotated=is_rotated, is_beam4=(beam==2), Rr=0.017)
    env['on_b2s'] = store_val_on_b2s


def assign_spool_pieces(env):
    arc_map = {
        ('r', '1'): 12, ('l', '2'): 12,
        ('r', '2'): 23, ('l', '3'): 23,
        ('r', '3'): 34, ('l', '4'): 34,
        ('r', '4'): 45, ('l', '5'): 45,
        ('r', '5'): 56, ('l', '6'): 56,
        ('r', '6'): 67, ('l', '7'): 67,
        ('r', '7'): 78, ('l', '8'): 78,
        ('r', '8'): 81, ('l', '1'): 81
    }
    mb_pattern = re.compile(r"mb\.\w+([rl])([1-8])\.\w+")
    mcs_pattern = re.compile(r"mcs\.\w*([rl])([1-8])\.\w+")
    mco_pattern = re.compile(r"mco\.\w*([rl])([1-8])\.\w+")
    mcd_pattern = re.compile(r"mcd\.\w*([rl])([1-8])\.\w+")

    mb_per_arc = []
    mcs_per_arc = []
    mco_per_arc = []
    mcd_per_arc = []
    for beam in ["lhcb1", "lhcb2"]:
        mb_per_arc.append(defaultdict(list))
        mcs_per_arc.append(defaultdict(list))
        mco_per_arc.append(defaultdict(list))
        mcd_per_arc.append(defaultdict(list))

        for name in env[beam].element_names:
            match_mb = mb_pattern.fullmatch(name)
            match_mcs = mcs_pattern.fullmatch(name)
            match_mco = mco_pattern.fullmatch(name)
            match_mcd = mcd_pattern.fullmatch(name)
            
            if match_mb:
                letter, digit = match_mb.groups()
                arc = arc_map.get((letter, digit))
                if arc:
                    if env[name].to_dict()["__class__"] == "Drift":
                        continue
                    mb_per_arc[-1][arc].append(name)
            elif match_mcs:
                letter, digit = match_mcs.groups()
                arc = arc_map.get((letter, digit))
                if arc:
                    if env[name].to_dict()["__class__"] == "Drift":
                        continue
                    mcs_per_arc[-1][arc].append(name)
            elif match_mco:
                letter, digit = match_mco.groups()
                arc = arc_map.get((letter, digit))
                if arc:
                    if env[name].to_dict()["__class__"] == "Drift":
                        continue
                    mco_per_arc[-1][arc].append(name)
            elif match_mco:
                letter, digit = match_mco.groups()
                arc = arc_map.get((letter, digit))
                if arc:
                    if env[name].to_dict()["__class__"] == "Drift":
                        continue
                    mco_per_arc[-1][arc].append(name)
            elif match_mcd:
                letter, digit = match_mcd.groups()
                arc = arc_map.get((letter, digit))
                if arc:
                    if env[name].to_dict()["__class__"] == "Drift":
                        continue
                    mcd_per_arc[-1][arc].append(name)
            else:
                continue

    for arc in [12, 23, 34, 45, 56, 67, 78, 81]:
        for beam in [1, 2]:
            total_k2l = 0.0
            total_k3l = 0.0
            total_k4l = 0.0

            for name in mb_per_arc[beam-1][arc]:
                total_k2l += env[name].knl[2]
                total_k3l += env[name].knl[3]
                total_k4l += env[name].knl[4]

            k2l_corr = total_k2l / len(mcs_per_arc[arc]) if len(mcs_per_arc[arc]) != 0 else 0 
            k3l_corr = total_k3l / len(mco_per_arc[arc]) if len(mco_per_arc[arc]) != 0 else 0
            k4l_corr = total_k4l / len(mcd_per_arc[arc]) if len(mcd_per_arc[arc]) != 0 else 0

            if beam == 1:
                kcs = -k2l_corr / env.vv["l.mcs"]
                kco = -k3l_corr / env.vv["l.mco"]
                kcd = -k4l_corr / env.vv["l.mcd"]
            else:
                kcs = k2l_corr / env.vv["l.mcs"]
                kco = k3l_corr / env.vv["l.mco"]
                kcd = k4l_corr / env.vv["l.mcd"]

            if np.isfinite(kcs):
                env.vv[f"kcs.a{arc}b{beam}"] = kcs
            if np.isfinite(kco):
                env.vv[f"kco.a{arc}b{beam}"] = kco
            if np.isfinite(kcd):
                env.vv[f"kcd.a{arc}b{beam}"] = kcd


def consider_micado(env):
    if env.vars['on_errors'] and (env['on_a1s'])**2 + (env['on_a1r'])**2 \
                               + (env['on_b1s'])**2 + (env['on_b1r'])**2 > 0:
        print("Correcting trajectory with Micado")
        for line in env.lines.values():
            env.vars['on_errors'] = 0
            tw_ref = line.twiss()
            env.vars['on_errors'] = 1
            line.correct_trajectory(twiss_table=tw_ref, n_micado=5, n_iter=1)


def _get_name_from_slot(name, error_list, env):
    beam = int(round(error_list['beam']))
    if beam == 0:
        name_match = name
    elif name[:-1].endswith('.v'):
        name_match = name[:-3]
    else:
        name_match = name
    magnets = []
    for nn in env.elements.keys():
        if name_match in nn:
            magnets.append(nn)
    return name_match, beam, magnets

def _extend_order_knl_ksl(env, pattern, order=_MAX_ORDER):
    # Some magnets are unplugged from the lattice (put as Drifts).
    # With this function we extend the knl/ksl arrays but skip the unplugged.
    for line in env.lines.values():
        tt = line.get_table()
        mask = ~np.array([nn.startswith('Limit') or nn.startswith('Drift') or nn.startswith('Marker')
                          for nn in tt.element_type])
        line.extend_knl_ksl(order=order, element_names=list(tt.rows[mask].rows[pattern].name))

def _veto_for_errors(env):
    # Get all the unplugged magnets in both lines.
    veto = np.array([])
    if 'lhcb1' in env.lines:
        tt_1 = env['lhcb1'].get_table()
        mask = np.array([nn.startswith('Limit') or nn.startswith('Drift') or nn.startswith('Marker')
                        for nn in tt_1.element_type])
        veto = np.concatenate((veto, tt_1.rows[mask].name))
    if 'lhcb2' in env.lines:
        tt_2 = env['lhcb2'].get_table()
        mask = np.array([nn.startswith('Limit') or nn.startswith('Drift') or nn.startswith('Marker')
                        for nn in tt_2.element_type])
        veto = np.concatenate((veto, tt_2.rows[mask].name))
    return veto

def _is_rotated(name, rotation_table):
    if name in rotation_table:
        return np.isclose(rotation_table[name]['YROTA'], 180)
    else:
        return False
