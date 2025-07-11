from tfs_tools import read_table

def compare_error_tables(ref, new, match=True):
    import numpy as np
    ref = read_table(ref)
    new = read_table(new)
    refnames = list(ref.keys())
    for nn, vv in new.items():
        names = [nnn for nnn in refnames if nn[1:-1] in nnn]
        if len(names) == 0:
            print(f"Warning: {nn} not in reference table")
        all_fine = True
        for kk, vvv in vv.items():
            refkk = np.sum([ref[nnn][kk] for nnn in names])
            if np.isclose(refkk, 0):
                if not np.isclose(vvv, 0):
                    print(f"Warning: {nn} not assigned in reference table")
                    break
            else:
                if nn.startswith('mb') or nn.startswith('mq'):
                    if not np.isclose(vvv, refkk):
                        all_fine = False
                        break
                else:
                    # Reference strengths are not exactly the same due to different matching
                    if np.abs((vvv - refkk)/refkk) > 0.1:
                        all_fine = False
                        break
            if np.sign(vvv) != np.sign(refkk):
                all_fine = False
                break
        if not all_fine and match:
            print(f"{nn}  and  {names}  do not match!")
        if all_fine and not match:
            print(f"{nn}  and  {names}  do match!")

# new = read_table('temp/MB_lhcb2.errors')
# ref = read_table('temp/MB_lhcb2_ref.errors')
# name = 'ms.28l1.b2'
# for kk, vv in new[name].items():
#     print(f"{kk}:   {vv}  vs  {ref[f'{name}'][kk]}")
