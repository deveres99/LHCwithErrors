import numpy as np
from pathlib import Path
from math import factorial


def add_error_knobs(env):
    if 'on_errors' not in env.vars: env['on_errors'] = 1
    for i in range(1, 3):
        if f'on_a{i}s' not in env.vars: env[f'on_a{i}s'] = 0
        if f'on_a{i}r' not in env.vars: env[f'on_a{i}r'] = 0
        if f'on_b{i}s' not in env.vars: env[f'on_b{i}s'] = 0
        if f'on_b{i}r' not in env.vars: env[f'on_b{i}r'] = 0
    for i in range(3, 16):
        if f'on_a{i}s' not in env.vars: env[f'on_a{i}s'] = 1
        if f'on_a{i}r' not in env.vars: env[f'on_a{i}r'] = 1
        if f'on_b{i}s' not in env.vars: env[f'on_b{i}s'] = 1
        if f'on_b{i}r' not in env.vars: env[f'on_b{i}r'] = 1


def extend_order_knl_ksl(env, pattern, order=20):
    for line in env.lines.values():
        tt = line.get_table()
        mask = ~np.array([nn.startswith('Limit') or nn.startswith('Drift') or nn.startswith('Marker')
                          for nn in tt.element_type])
        line.extend_knl_ksl(order=order, element_names=list(tt.rows[mask].rows[pattern].name))


def veto_for_errors(env):
    tt_1 = env['lhcb1'].get_table()
    mask = np.array([nn.startswith('Limit') or nn.startswith('Drift') or nn.startswith('Marker')
                     for nn in tt_1.element_type])
    veto = tt_1.rows[mask].name
    tt_2 = env['lhcb2'].get_table()
    mask = np.array([nn.startswith('Limit') or nn.startswith('Drift') or nn.startswith('Marker')
                     for nn in tt_2.element_type])
    return np.concatenate((veto, tt_2.rows[mask].name))


def assign_bend_errors(env, name, error_list, rotation_table, veto=None, Rr=0.017):
    name, beam, magnets = _get_name_from_slot(name, error_list)
    order = 0
    yfac = -1 if beam == 2 else 1
    if name in rotation_table:
        if np.isclose(rotation_table[name]['YROTA'], 180):
            yfac *= -1
    for this_name in magnets:
        if this_name not in env.elements:
            print(); print(f"Warning: {this_name} not found in environment, not assigning errors.")
            continue
        if veto is not None and this_name in veto:
            print(); print(f"Warning: {this_name} on veto list, not assigning errors.")
            continue
        print(this_name, end=' ')
        bn_s = [-error_list[f'b{i}']*yfac if i%2==0 else error_list[f'b{i}'] for i in range(1, 21) if f'b{i}' in error_list]
        an_s = [-error_list[f'a{i}']*yfac if i%2==1 else error_list[f'a{i}'] for i in range(1, 21) if f'a{i}' in error_list]
        for i, bn in enumerate(bn_s):
            env[this_name].knl[i] += bn * env.vars['on_errors'] * env.vars[f'on_b{i+1}s'] * 1e-4 * env.ref[this_name].k0 * (Rr**(order-i)) * factorial(i) / factorial(order)
        for i, an in enumerate(an_s):
            env[this_name].ksl[i] += an * env.vars['on_errors'] * env.vars[f'on_a{i+1}s'] * 1e-4 * env.ref[this_name].k0 * (Rr**(order-i)) * factorial(i) / factorial(order)


def assign_quad_errors(env, name, error_list, rotation_table, veto=None, Rr=0.017):
    name, beam, magnets = _get_name_from_slot(name, error_list)
    order = 1
    yfac = -1 if beam == 2 else 1
    sfac = 1
    if name in rotation_table:
        if np.isclose(rotation_table[name]['YROTA'], 180):
            yfac *= -1
        if np.isclose(rotation_table[name]['SROTA'], 180):
            sfac *= -1
    for this_name in magnets:
        if this_name not in env.elements:
            print(); print(f"Warning: {this_name} not found in environment, not assigning errors.")
            continue
        if veto is not None and this_name in veto:
            print(); print(f"Warning: {this_name} on veto list, not assigning errors.")
            continue
        print(this_name, end=' ')
        bn_s = [-error_list[f'b{i}']*yfac*sfac if i%2==1 else error_list[f'b{i}'] for i in range(1, 21) if f'b{i}' in error_list]
        an_s = [-error_list[f'a{i}']*yfac      if i%2==0 else error_list[f'a{i}']*sfac for i in range(1, 21) if f'a{i}' in error_list]
        for i, bn in enumerate(bn_s):
            env[this_name].knl[i] += bn * env.vars['on_errors'] * env.vars[f'on_b{i+1}s'] * 1e-4 * env.ref[this_name].k1 * (Rr**(order-i)) * factorial(i) / factorial(order)
        for i, an in enumerate(an_s):
            env[this_name].ksl[i] += an * env.vars['on_errors'] * env.vars[f'on_a{i+1}s'] * 1e-4 * env.ref[this_name].k1 * (Rr**(order-i)) * factorial(i) / factorial(order)


def assign_sext_errors(env, name, error_list, rotation_table, veto=None, Rr=0.017):
    name, beam, magnets = _get_name_from_slot(name, error_list)
    order = 2
    yfac = -1 if beam == 2 else 1
    if name in rotation_table:
        if np.isclose(rotation_table[name]['YROTA'], 180):
            yfac *= -1
    for this_name in magnets:
        if this_name not in env.elements:
            print(); print(f"Warning: {this_name} not found in environment, not assigning errors.")
            continue
        if veto is not None and this_name in veto:
            print(); print(f"Warning: {this_name} on veto list, not assigning errors.")
            continue
        print(this_name, end=' ')
        bn_s = [-error_list[f'b{i}']*yfac if i%2==0 else error_list[f'b{i}'] for i in range(1, 21) if f'b{i}' in error_list]
        an_s = [-error_list[f'a{i}']*yfac if i%2==1 else error_list[f'a{i}'] for i in range(1, 21) if f'a{i}' in error_list]
        for i, bn in enumerate(bn_s):
            env[this_name].knl[i] += bn * env.vars['on_errors'] * env.vars[f'on_b{i+1}s'] * 1e-4 * env.ref[this_name].k2 * (Rr**(order-i)) * factorial(i) / factorial(order)
        for i, an in enumerate(an_s):
            env[this_name].ksl[i] += an * env.vars['on_errors'] * env.vars[f'on_a{i+1}s'] * 1e-4 * env.ref[this_name].k2 * (Rr**(order-i)) * factorial(i) / factorial(order)


def assign_skew_sext_errors(env, name, error_list, rotation_table, veto=None, Rr=0.017):
    name, beam, magnets = _get_name_from_slot(name, error_list)
    order = 2
    yfac = -1 if beam == 2 else 1
    if name in rotation_table:
        if np.isclose(rotation_table[name]['YROTA'], 180):
            yfac *= -1
    for this_name in magnets:
        if this_name not in env.elements:
            print(); print(f"Warning: {this_name} not found in environment, not assigning errors.")
            continue
        if veto is not None and this_name in veto:
            print(); print(f"Warning: {this_name} on veto list, not assigning errors.")
            continue
        print(this_name, end=' ')
        bn_s = [error_list[f'b{i}']*yfac if i%2==0 else -error_list[f'b{i}'] for i in range(1, 21) if f'b{i}' in error_list]
        an_s = [error_list[f'a{i}']*yfac if i%2==1 else -error_list[f'a{i}'] for i in range(1, 21) if f'a{i}' in error_list]
        for i, bn in enumerate(bn_s):
            env[this_name].knl[i] += bn * env.vars['on_errors'] * env.vars[f'on_b{i+1}s'] * 1e-4 * env.ref[this_name].k2s * (Rr**(order-i)) * factorial(i) / factorial(order)
        for i, an in enumerate(an_s):
            env[this_name].ksl[i] += an * env.vars['on_errors'] * env.vars[f'on_a{i+1}s'] * 1e-4 * env.ref[this_name].k2s * (Rr**(order-i)) * factorial(i) / factorial(order)


def assign_oct_errors(env, name, error_list, rotation_table, veto=None, Rr=0.017):
    name, beam, magnets = _get_name_from_slot(name, error_list)
    order = 3
    yfac = -1 if beam == 2 else 1
    if name in rotation_table:
        if np.isclose(rotation_table[name]['YROTA'], 180):
            yfac *= -1
    for this_name in magnets:
        if this_name not in env.elements:
            print(); print(f"Warning: {this_name} not found in environment, not assigning errors.")
            continue
        if veto is not None and this_name in veto:
            print(); print(f"Warning: {this_name} on veto list, not assigning errors.")
            continue
        print(this_name, end=' ')
        bn_s = [-error_list[f'b{i}']*yfac if i%2==1 else error_list[f'b{i}'] for i in range(1, 21) if f'b{i}' in error_list]
        an_s = [-error_list[f'a{i}']*yfac if i%2==0 else error_list[f'a{i}'] for i in range(1, 21) if f'a{i}' in error_list]
        for i, bn in enumerate(bn_s):
            env[this_name].knl[i] += bn * env.vars['on_errors'] * env.vars[f'on_b{i+1}s'] * 1e-4 * env.ref[this_name].k3 * (Rr**(order-i)) * factorial(i) / factorial(order)
        for i, an in enumerate(an_s):
            env[this_name].ksl[i] += an * env.vars['on_errors'] * env.vars[f'on_a{i+1}s'] * 1e-4 * env.ref[this_name].k3 * (Rr**(order-i)) * factorial(i) / factorial(order)


def do_micado(env):
    if env.vars['on_errors'] and (env['on_a1s'])**2 + (env['on_a1r'])**2 \
                               + (env['on_b1s'])**2 + (env['on_b1r'])**2 > 0:
        print("Correcting trajectory with Micado")
        for line in env.lines.values():
            env.vars['on_errors'] = 0
            tw_ref = line.twiss()
            env.vars['on_errors'] = 1
            line.correct_trajectory(twiss_table=tw_ref, n_micado=5, n_iter=1)


def _get_name_from_slot(name, error_list):
    beam = int(round(error_list['beam']))
    if beam == 0:
        magnets = [f'{name}/lhcb1', f'{name}/lhcb2']
    elif name[:-1].endswith('.v'):
        name = name[:-3]
        magnets = [f"{name}.b{beam}"]
    else:
        magnets = [f"{name}.b{beam}"]
    return name, beam, magnets
