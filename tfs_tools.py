from math import floor, log10
from pathlib import Path


def store_twiss_reference(env):
    for linename, line in env.lines.items():
        tt = line.get_table(attr=True)
        tw = line.twiss()
        lines = []
        lines.append('@ NAME             %05s "TWISS"')
        lines.append('@ TYPE             %05s "TWISS"')
        lines.append(f'@ SEQUENCE         %05s "{linename.upper()}"')
        energy = int(round(line.particle_ref.energy[0] / 1e9))
        lines.append(f'@ ENERGY           %le                 {energy}')
        lines.append("* NAME                              K0L                K1L               BETX               BETY                 DX                MUX                MUY ")
        lines.append("$ %s                                %le                %le                %le                %le                %le                %le                %le ")
        for nn, et, k0l, k1l, betx, bety, dx, mux, muy in zip(tt.name, tt.element_type, tt.k0l, tt.k1l, tw.betx, tw.bety, tw.dx, tw.mux, tw.muy):
            if et.startswith('Drift') or et.startswith('Limit') or et.startswith('Marker'):
                continue
            if nn.startswith('mb.') or nn.startswith('mbh.') or nn.startswith('mqt.14') \
            or nn.startswith('mqt.15') or nn.startswith('mqt.16') or nn.startswith('mqt.17') \
            or nn.startswith('mqt.18') or nn.startswith('mqt.19') or nn.startswith('mqt.20') \
            or nn.startswith('mqt.21') or nn.startswith('mqs.') or nn.startswith('mss.') \
            or nn.startswith('mco.') or nn.startswith('mcd.') or nn.startswith('mcs.'):
                mess  = f' "{nn.upper()}"'
                mess  = f'{mess:20}'
                mess += f'     {_format_fortran_float(k0l)}     {_format_fortran_float(k1l)}'
                mess += f'     {_format_fortran_float(betx)}     {_format_fortran_float(bety)}'
                mess += f'     {_format_fortran_float(dx)}     {_format_fortran_float(mux)}'
                mess += f'     {_format_fortran_float(muy)}'
                lines.append(mess)
        Path('temp').mkdir(parents=True, exist_ok=True)
        with Path(f'temp/optics0_MB_{linename}.mad').open('w') as fp:
            fp.write('\n'.join(lines) + '\n')


def read_table(filename):
    with Path(filename).open('r') as fp:
        result = {}
        for line in fp.readlines():
            line = line.strip()
            if line.startswith('@') or line.startswith('$'):
                continue
            elif line.startswith('*'):
                header = line.split()[1:]
            else:
                parts = line.split()
                if parts[0].lower() == 'not_found' \
                or [parts[0].lower(), parts[1].lower()] == ['not', 'found']:
                    continue
                vals = {kk: float(vv) for kk, vv in zip(header[1:], parts[1:])}
                result[parts[0].replace('"', '').lower()] = vals
    return result


def store_errors(env, pattern=['mb.*', 'mbh.*']):
    pattern = [patt.replace('*', '') for patt in pattern]  # TODO: use table rows instead of loop
    for linename, line in env.lines.items():
        tt = line.get_table(attr=True)
        lines = ['@ NAME             %06s "EFIELD"']
        lines.append('@ TYPE             %06s "EFIELD"')
        mess_col   = '* NAME                              K0L               K0SL                K1L               '
        mess_col  += 'K1SL                K2L               K2SL                K3L               K3SL                '
        mess_col  += 'K4L               K4SL                K5L               K5SL                K6L               '
        mess_col  += 'K6SL                K7L               K7SL                K8L               K8SL                '
        mess_col  += 'K9L               K9SL               K10L              K10SL               K11L              '
        mess_col  += 'K11SL               K12L              K12SL               K13L              K13SL               '
        mess_col  += 'K14L              K14SL               K15L              K15SL               K16L              '
        mess_col  += 'K16SL               K17L              K17SL               K18L              K18SL               '
        mess_col  += 'K19L              K19SL               K20L              K20SL '
        lines.append(mess_col)
        mess_type  = '$ %s                                %le                %le                %le                '
        mess_type += '%le                %le                %le                %le                %le                '
        mess_type += '%le                %le                %le                %le                %le                '
        mess_type += '%le                %le                %le                %le                %le                '
        mess_type += '%le                %le                %le                %le                %le                '
        mess_type += '%le                %le                %le                %le                %le                '
        mess_type += '%le                %le                %le                %le                %le                '
        mess_type += '%le                %le                %le                %le                %le                '
        mess_type += '%le                %le                %le                %le '
        lines.append(mess_type)
        for nn, et in zip(tt.name, tt.element_type):
            if et.startswith('Drift') or et.startswith('Limit') or et.startswith('Marker'):
                continue
            if any([nn.startswith(patt) for patt in pattern]):
                mess  = f' "{nn.upper()}"'
                mess  = f'{mess:20}'
                knl = line[nn].knl
                ksl = line[nn].ksl
                for i in range(21):
                    knli = knl[i] if i < len(knl) else 0.0
                    ksli = ksl[i] if i < len(ksl) else 0.0
                    mess += f'     {_format_fortran_float(knli)}     {_format_fortran_float(ksli)}'
                lines.append(mess)
        Path('temp').mkdir(parents=True, exist_ok=True)
        with Path(f'temp/MB_{linename}.errors').open('w') as fp:
            fp.write('\n'.join(lines) + '\n')


def _format_fortran_float(value, n_digits=14):
    if abs(value) > 9.99e99:
        raise ValueError(f"Value {value} is too large.")
    elif abs(value) < 1e-99:
        return f"{'0.0':>{n_digits}}"
    if 1.e-4 <= value <= 999999999. or -1.e-4 >= value >= -99999999.:
        max_digits = n_digits-2 if value > 0 else n_digits-3
        n_decimal_digits = int(max_digits - max(floor(log10(abs(value))), 0))
        value_string = f"{value:{n_digits}.{n_decimal_digits}f}"
        value_splitted = value_string.split('.')
        if len(value_splitted) == 1:
            return f"{value_string[1:]}."
        else:
            decimals = value_splitted[1]
            while decimals[-1] == '0':
                decimals = decimals[:-1]
                if decimals == '':
                    decimals = '0'
                    break
            value_string = f"{value_splitted[0]}.{decimals}"
            return f"{value_string:>{n_digits}}"
    else:
        max_digits = n_digits-6 if value > 0 else n_digits-7
        value_string = f"{value:.{max_digits}E}"
        value_splitted = value_string.split('E')
        value_splitted_mant = value_splitted[0].split('.')
        if len(value_splitted_mant) == 1:
            return value_string
        else:
            decimals = value_splitted_mant[1]
            dot = '.'
            while decimals[-1] == '0':
                decimals = decimals[:-1]
                if decimals == '':
                    dot = ''
                    break
            value_string = f"{value_splitted_mant[0]}{dot}{decimals}E{value_splitted[1]}"
            return f"{value_string:>{n_digits}}"
