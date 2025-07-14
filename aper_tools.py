import numpy as np
import re
import xtrack as xt

bad_apertures_in_layout_db = [
    "vcrlb.1l2.a.b1", 
    "vcrlb.1l2.b.b1", 
    "vcrlb.1l2.c.b1", 
    "vcrlb.1l2.d.b1", 
    "vc2ud.d1l2.a.b1", 
    "vc2ud.d1l2.b.b1", 
    "vc2ud.c1l2.a.b1", 
    "vc2ud.c1l2.b.b1", 
    "vc2uc.a1l2.a.b1", 
    "vc2uc.a1l2.b.b1", 
    "vcdaj.a1l2.a.b1", 
    "vcdaj.a1l2.b.b1", 
    "vc2c.a1l2.a.b1", 
    "vc2c.a1l2.b.b1", 
    "vc2aa.a1r2.a.b1", 
    "vc2aa.a1r2.b.b1", 
    "vcrlb.1r2.a.b1", 
    "vcrlb.1r2.b.b1", 
    "vcrlb.1r2.c.b1", 
    "vcrlb.1r2.d.b1", 
    "vcrla.a1l8.a.b1", 
    "vcrla.a1l8.b.b1", 
    "vcrld.1l8.a.b1", 
    "vcrld.1l8.b.b1", 
    "vcdbu.1l8.a.b1", 
    "vcdbu.1l8.b.b1", 
    "vcda.1l8.a.b1", 
    "vcda.1l8.b.b1", 
    "vcrlc.a1l8.a.b1", 
    "vcrlc.a1l8.b.b1", 
    "vcrlg.1l8.a.b1", 
    "vcrlg.1l8.b.b1", 
    "vcdav.1l8.a.b1", 
    "vcdav.1l8.b.b1", 
    "vc8a.1r8.a.b1", 
    "vc8a.1r8.b.b1", 
    "vc8b.1r8.a.b1", 
    "vc8b.1r8.b.b1", 
    "vc8c.1r8.a.b1", 
    "vc8d.1r8.a.b1", 
    "vc8d.1r8.b.b1", 
    "vc8e.1r8.a.b1", 
    "vc8c.1r8.b.b1", 
    "vc8e.1r8.b.b1", 
    "vc8f.1r8.a.b1", 
    "vc8f.1r8.b.b1", 
    "vc8g.a1r8.a.b1", 
    "vc8ga.a1r8.a.b1", 
    "vc8g.a1r8.b.b1", 
    "vc8ga.a1r8.b.b1", 
    "vcrld.1r8.a.b1", 
    "vcrld.1r8.b.b1", 
    "vcrla.a1r8.a.b1", 
    "vcrla.a1r8.b.b1", 
    "vcrla.a1r8.b.b2", 
    "vcrld.1r8.b.b2", 
    "vcrla.a1r8.a.b2", 
    "vcrld.1r8.a.b2", 
    "vc8g.a1r8.b.b2", 
    "vc8ga.a1r8.b.b2", 
    "vc8f.1r8.b.b2", 
    "vc8g.a1r8.a.b2", 
    "vc8ga.a1r8.a.b2", 
    "vc8e.1r8.b.b2", 
    "vc8f.1r8.a.b2", 
    "vc8c.1r8.b.b2", 
    "vc8d.1r8.b.b2", 
    "vc8e.1r8.a.b2", 
    "vc8d.1r8.a.b2", 
    "vc8c.1r8.a.b2", 
    "vc8b.1r8.b.b2", 
    "vc8a.1r8.b.b2", 
    "vc8b.1r8.a.b2", 
    "vc8a.1r8.a.b2", 
    "vcdav.1l8.b.b2", 
    "vcdav.1l8.a.b2", 
    "vcrlg.1l8.b.b2", 
    "vcrlg.1l8.a.b2", 
    "vcrlc.a1l8.b.b2", 
    "vcrlc.a1l8.a.b2", 
    "vcda.1l8.b.b2", 
    "vcda.1l8.a.b2", 
    "vcdbu.1l8.b.b2", 
    "vcdbu.1l8.a.b2", 
    "vcrld.1l8.b.b2", 
    "vcrla.a1l8.b.b2", 
    "vcrld.1l8.a.b2", 
    "vcrla.a1l8.a.b2", 
    "vcrlb.1r2.d.b2", 
    "vcrlb.1r2.c.b2", 
    "vcrlb.1r2.b.b2", 
    "vcrlb.1r2.a.b2", 
    "vc2aa.a1r2.b.b2", 
    "vc2aa.a1r2.a.b2", 
    "vc2c.a1l2.b.b2", 
    "vc2c.a1l2.a.b2", 
    "vcdaj.a1l2.b.b2", 
    "vcdaj.a1l2.a.b2", 
    "vc2uc.a1l2.b.b2", 
    "vc2uc.a1l2.a.b2", 
    "vc2ud.c1l2.b.b2", 
    "vc2ud.c1l2.a.b2", 
    "vc2ud.d1l2.b.b2", 
    "vc2ud.d1l2.a.b2", 
    "vcrlb.1l2.d.b2", 
    "vcrlb.1l2.c.b2", 
    "vcrlb.1l2.b.b2", 
    "vcrlb.1l2.a.b2", 
]

def parse_aperture_sequence(path, beam, apertypes, elements):
    apertype_pattern = re.compile(
        r"^([A-Za-z0-9]+):\s*marker,\s*apertype=\s*([A-Za-z]+),\s*aperture=\s*{\s*([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)\s*};$"
    )
    element_pattern1 = re.compile(r"^([\w\.]+):\s*([A-Za-z0-9]+),\s*aper_tol:=\{\s*([A-Za-z]+),\s*([A-Za-z]+),\s*([A-Za-z]+)\s*\},\s*mech_sep=\s*(-?[\d.]+),\s*v_pos=\s*(-?[\d.]+),\s*aper_tilt=\s*(-?[\d.]+)\*PI/180,\s*slot_id=\s*(\d+);$")
    element_pattern2 = re.compile(r"^([\w\.]+):\s*([A-Za-z0-9]+),\s*aper_tol:=\{\s*([A-Za-z]+),\s*([A-Za-z]+),\s*([A-Za-z]+)\s*\},\s*mech_sep=\s*(-?[\d.]+),\s*v_pos=\s*(-?[\d.]+),\s*aper_tilt=\s*(-?[\d.]+)\*PI/180,\s*slot_id=\s*(\d+),\s*assembly_id=\s*(\d+);$")
    install_pattern = re.compile(r"^install,\s*element\s*=\s*([\w\.]+),\s*at=\s*([\w\d\.\+\-\*/\(\)]+),\s*from=\s*([A-Za-z0-9\.]+);$")
    
    with open(path, "r") as file:
        for line in file:
            line = line.strip()
            
            apertype_match = apertype_pattern.match(line)
            if apertype_match:
                groups = apertype_match.groups()
                if groups[1] == "ELLIPSE":
                    apertypes[groups[0]] = xt.LimitEllipse(
                        a=float(groups[2]), 
                        b=float(groups[3])
                    )
                elif groups[1] == "RECTANGLE":
                    apertypes[groups[0]] = xt.LimitRect(
                        min_x=-float(groups[2]), 
                        max_x=float(groups[2]), 
                        min_y=-float(groups[3]), 
                        max_y=float(groups[3])
                    )
                elif groups[1] == "CIRCLE":
                    apertypes[groups[0]] = xt.LimitEllipse(
                        a=float(groups[2]), 
                        b=float(groups[2])
                    )
                elif groups[1] == "RECTELLIPSE":
                    apertypes[groups[0]] = xt.LimitRectEllipse(
                        max_x=float(groups[2]), 
                        max_y=float(groups[2]), 
                        a=float(groups[4]), 
                        b=float(groups[5])
                    )
                elif groups[1] == "RACETRACK":
                    apertypes[groups[0]] = xt.LimitRacetrack(
                        min_x=-float(groups[2]), 
                        max_x=float(groups[2]), 
                        min_y=-float(groups[3]), 
                        max_y=float(groups[3]), 
                        a=float(groups[4]), 
                        b=float(groups[5])
                    )
                else:
                    raise ValueError(f"Unrecognised aperture type: {groups[0]}")

            element_match = element_pattern1.match(line)
            if element_match:
                groups = element_match.groups()
                if not groups[0].lower().endswith(f".{beam}"):
                    continue
                elements[groups[0].lower()] = {
                    "type": groups[1], 
                    "mech_sep": float(groups[5]), 
                    "v_pos": float(groups[6]), 
                    "tilt": float(groups[7])
                }

            element_match = element_pattern2.match(line)
            if element_match:
                groups = element_match.groups()
                if not groups[0].lower().endswith(f".{beam}"):
                    continue
                elements[groups[0].lower()] = {
                    "type": groups[1], 
                    "mech_sep": float(groups[5]), 
                    "v_pos": float(groups[6]), 
                    "tilt": float(groups[7])
                }

            install_match = install_pattern.match(line)
            if install_match:
                groups = install_match.groups()
                if not groups[0].lower().endswith(f".{beam}"):
                    continue
                elements[groups[0].lower()]["at"] = groups[1].lower()
                elements[groups[0].lower()]["from"] = groups[2].lower()

    return apertypes, elements

def apply_corrections(path, elements):
    remove_pattern = re.compile(r"^remove,element=([\w\.]+);$")

    with open(path, "r") as file:
        for line in file:
            line = line.strip()
            
            remove_match = remove_pattern.match(line)
            if remove_match:
                groups = remove_match.groups()
                try:
                    del elements[groups[0].lower()]
                except KeyError:
                    continue

    for nn in bad_apertures_in_layout_db:
        try:
            del elements[nn]
        except KeyError:
            continue

    return elements

def install_apertures(env, apertypes_b1, apertypes_b2, elements_b1, elements_b2):
    for key, value in elements_b1.items():
        env.elements[key] = apertypes_b1[value["type"]]
    
    for key, value in elements_b2.items():
        env.elements[key] = apertypes_b2[value["type"]]

    insert_list_b1 = [env.place(nn, at=elements_b1[nn]["at"], from_=elements_b1[nn]["from"]) for nn in elements_b1.keys()]
    insert_list_b2 = [env.place(nn, at=elements_b2[nn]["at"], from_=elements_b2[nn]["from"]) for nn in elements_b2.keys()]
    
    env["lhcb1"].insert(insert_list_b1, s_tol=2e-6)
    env["lhcb2"].insert(insert_list_b2, s_tol=2e-6)

def offset_apertures(env, elements_b1, elements_b2):
    straight_lhcb1 = env["lhcb1"].copy()
    straight_lhcb2 = env["lhcb2"].copy()
    straight_lhcb1.vv["a.mb"] = 0.0
    straight_lhcb2.vv["a.mb"] = 0.0
    surv_b1 = straight_lhcb1.survey()
    surv_b2 = straight_lhcb2.survey(reverse=False)

    for nn in elements_b1.keys():
        # env["lhcb1"][nn].rot_s_rad = elements_b1[nn]["tilt"] * np.pi / 180
        env["lhcb1"][nn].shift_y = elements_b1[nn]["v_pos"]
        env["lhcb1"][nn].shift_x = elements_b1[nn]["mech_sep"] / 2.0 - surv_b1.rows[nn]["X"][0]

    for nn in elements_b2.keys():
        # env["lhcb2"][nn].rot_s_rad = elements_b2[nn]["tilt"] * np.pi / 180
        env["lhcb2"][nn].shift_y = elements_b2[nn]["v_pos"]
        env["lhcb2"][nn].shift_x = elements_b2[nn]["mech_sep"] / 2.0 - surv_b2.rows[nn]["X"][0]