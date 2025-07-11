# Compare to a stored reference (from MAD-X)
store_errors(env, pattern=['mb.*', 'mbh.*', 'mq.*', 'ms.*', 'mss.*', 'mo.*'])

compare_error_tables('temp/MB_lhcb1_ref.errors', 'temp/MB_lhcb1.errors')

