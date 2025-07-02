

# TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
# TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
# TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
# TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

print("TODO TODO: aperture not yet implemented")

# Load the environment and the configuration
env = xt.Environment.from_json('lattices/injection_clean.json')

# Step one: add all apertures from elements and from LayoutDB
# Step two: misalign aperture and elements based on the mech_sep (is important in the doglegs, both for
#           aperture and feeddown effects from errors)

# Save the environment
env.to_json('lattices/injection_with_apertures.json')
