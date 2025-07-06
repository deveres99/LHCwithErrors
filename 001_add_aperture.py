import xtrack as xt
from pathlib import Path
import time
start = time.time()


# Paths
path_acc_models = Path("/eos/project-c/collimation-team/machine_configurations/acc-models/lhc/2025")
path_layout = Path("/eos/project-c/collimation-team/machine_configurations/layoutdb")
infile = Path("lattices/injection_clean.json")
outfile = Path("lattices/injection_with_apertures.json")


# =================================================================================================

# Load the environment and the configuration
env = xt.Environment.from_json(infile)

# TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
# TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
# TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
# TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

print("TODO TODO: aperture not yet implemented")

# Step one: add all apertures from elements and from LayoutDB
# Step two: misalign aperture and elements based on the mech_sep (is important in the doglegs, both for
#           aperture and feeddown effects from errors)

# Save the environment
env.to_json(outfile)
print(f"Adding apertures took {time.time() - start:.2f} seconds")
