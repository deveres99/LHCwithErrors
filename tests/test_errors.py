import xtrack as xt
from pathlib import Path
from cpymad.madx import Madx

from knob_tools import disable_crossing
from tfs_tools import store_twiss_reference, store_errors
from error_tools import add_error_knobs, load_error_table, assign_errors
from comparison_tools import compare_error_tables


beam = 1
seed = 6

path_errors = Path("/eos/project-c/collimation-team/machine_configurations/lhcerrors")


# Make the line in MAD-X
mad = Madx()
mad.call(f"injection_b{beam}.madx")
sequence = 'lhcb1' if beam==1 else 'lhcb2'
line = xt.Line.from_madx_sequence(mad.sequence[sequence], apply_madx_errors=False, deferred_expressions=True)
env = xt.Environment(lines={'lhcb1':line})
env['lhcb1'].particle_ref = xt.Particles(mass0=xt.PROTON_MASS_EV, gamma0=mad.sequence[sequence].beam.gamma)
mad.input(f'''
on_disp = 0;

myseed               = {seed};
ver_lhc_run          = 3;
on_errors_LHC        = 1;
call, file="{path_errors.as_posix()}/LHC/Msubroutines.madx";
call, file="{path_errors.as_posix()}/LHC/Msubroutines_MS_MSS_MO.madx";
call, file="{path_errors.as_posix()}//Orbit_Routines.madx";
call, file="{path_errors.as_posix()}//SelectLHCMonCor_v1.madx";
call, file="{path_errors.as_posix()}/HL-LHC/macro_error_v1.madx";   ! macros for error generation in the new IT/D1's
exec, ON_ALL_MULT;
ON_A1s =  0 ; ON_A1r =  0 ; ON_B1s =  0 ; ON_B1r =  0 ;
ON_A2s =  0 ; ON_A2r =  0 ; ON_B2s =  0 ; ON_B2r =  0 ;
ON_A3s =  1 ; ON_A3r =  1 ; ON_B3s =  1 ; ON_B3r =  1 ;
ON_A4s =  1 ; ON_A4r =  1 ; ON_B4s =  1 ; ON_B4r =  1 ;
ON_A5s =  1 ; ON_A5r =  1 ; ON_B5s =  1 ; ON_B5r =  1 ;
ON_A6s =  1 ; ON_A6r =  1 ; ON_B6s =  1 ; ON_B6r =  1 ;
ON_A7s =  1 ; ON_A7r =  1 ; ON_B7s =  1 ; ON_B7r =  1 ;
ON_A8s =  1 ; ON_A8r =  1 ; ON_B8s =  1 ; ON_B8r =  1 ;
ON_A9s =  1 ; ON_A9r =  1 ; ON_B9s =  1 ; ON_B9r =  1 ;
ON_A10s = 1 ; ON_A10r = 1 ; ON_B10s = 1 ; ON_B10r = 1 ;
ON_A11s = 1 ; ON_A11r = 1 ; ON_B11s = 1 ; ON_B11r = 1 ;
ON_A12s = 1 ; ON_A12r = 1 ; ON_B12s = 1 ; ON_B12r = 1 ;
ON_A13s = 1 ; ON_A13r = 1 ; ON_B13s = 1 ; ON_B13r = 1 ;
ON_A14s = 1 ; ON_A14r = 1 ; ON_B14s = 1 ; ON_B14r = 1 ;
ON_A15s = 1 ; ON_A15r = 1 ; ON_B15s = 1 ; ON_B15r = 1 ;

twiss, table=nominal;   // used by orbit correction
beta.ip1=table(twiss,IP1,betx);value,beta.ip1;

! print nominal optics parameter at the MB, MQS and MSS for
! b2, b3, b4, b5, a2 and a3 correction
select, flag=twiss, clear;
select, flag=twiss,pattern=MB\.   ,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,pattern=MBH\.   ,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,pattern=MQT\.14,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,pattern=MQT\.15,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,pattern=MQT\.16,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,pattern=MQT\.17,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,pattern=MQT\.18,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,pattern=MQT\.19,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,pattern=MQT\.20,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,pattern=MQT\.21,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,class=MQS                      ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,class=MS                       ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,class=MSS                      ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,class=MO                       ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,class=MCO                      ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,class=MCD                      ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
select, flag=twiss,class=MCS                      ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
twiss,  file='temp/optics0_MB_lhcb{beam}_ref.mad';

! disable crossing bumps
exec, crossing_disable;

readtable, file="{path_errors.as_posix()}/LHC/rotations_Q2_integral.tab";
readtable, file="{path_errors.as_posix()}/LHC/wise/injection_errors-emfqcs-{seed}.tfs" ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MB.madx"  ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MBRB.madx";
call, file="{path_errors.as_posix()}/LHC/Efcomp_MBRC.madx";
call, file="{path_errors.as_posix()}/LHC/Efcomp_MBRS.madx";
call, file="{path_errors.as_posix()}/LHC/Efcomp_MBX.madx" ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MBXW.madx" ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MBW.madx" ;
ON_B2Saux=on_B2S;on_B2S=0;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MQW.madx" ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MQTL.madx";
call, file="{path_errors.as_posix()}/LHC/Efcomp_MQMC.madx";
call, file="{path_errors.as_posix()}/LHC/Efcomp_MQX.madx" ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MQY.madx" ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MQM.madx" ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MQML.madx";
call, file="{path_errors.as_posix()}/LHC/Efcomp_MQ.madx"  ;
on_B2S=ON_B2Saux;

readtable, file="{path_errors.as_posix()}/LHC/fidel/injection_errors-emfqcs-{seed}.tfs" ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MS.madx"  ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MSS.madx"  ;
call, file="{path_errors.as_posix()}/LHC/Efcomp_MO.madx"  ;

select, flag=error, clear;
select, flag=error, pattern=MB\.,class=multipole;
select, flag=error, pattern=MBH\.,class=multipole;
select, flag=error, pattern=MQ\.,class=multipole;
select, flag=error, pattern=MQS\.,class=multipole;
select, flag=error, pattern=MS\.,class=multipole;
select, flag=error, pattern=MSS\.,class=multipole;
select, flag=error, pattern=MO\.,class=multipole;
esave,  file="temp/MB_lhcb{beam}_ref.errors";
''')

# Add the errors in Xsuite
add_error_knobs(env)
store_twiss_reference(env)
disable_crossing(env)
tt_err, tt_rot = load_error_table(env, path_errors, seed, rotation_table=True)
assign_errors(env, tt_err, tt_rot, dipoles=True, separation_dipoles=True, quadrupoles=True)
tt_err = load_error_table(env, path_errors, seed, table_type='fidel')
assign_errors(env, tt_err, tt_rot, sextupoles=True, skew_sextupoles=True, octupoles=True)


store_errors(env, pattern=['mb.*', 'mbh.*', 'mq.*', 'ms.*', 'mss.*', 'mo.*'])

compare_error_tables(f'temp/MB_lhcb{beam}_ref.errors', f'temp/MB_lhcb{beam}.errors')

