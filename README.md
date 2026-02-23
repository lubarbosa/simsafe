# SimSafe

Integration framework coupling Hi-sAFe agroforestry model with SIMPLACE crop simulation platform.

## Overview

SimSafe enables spatially-explicit agroforestry simulations by:
- Running Hi-sAFe to simulate tree-crop interactions and microclimate
- Passing cell-specific weather conditions to SIMPLACE
- Running multi-cell crop simulations with AGROECO4CAST_AF
- Returning crop biomass to Hi-sAFe for feedback

## Project Structure

## Requirements

- Hi-sAFe (Capsis platform)
- SIMPLACE 5.x
- Python 3.8+
- Java 17

## Installation

See [docs/INSTALLATION.md](docs/INSTALLATION.md)

## Usage

See [docs/USAGE.md](docs/USAGE.md)

## License

[Specify your license]

## Authors

- Luciano Barbosa (@lubarbosa)

## Citation

[Add citation information when published]

## SIMPLACE Installation

This repository does not include SIMPLACE binaries. Download SIMPLACE separately:

1. Visit [SIMPLACE website](https://www.simplace.net/downloads)
2. Download SIMPLACE 5.x
3. Extract to `/path/to/SIMPLACE`
4. Update paths in `python/controllers/multi_cell_agroeco_controller.py`:
   ```python
   install_dir="/path/to/SIMPLACE"

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/lubarbosa/simsafe.git
cd simsafe
2. Install Hi-sAFe
Download and install Hi-sAFe via Capsis:

Visit http://capsis.cirad.fr/
Install Capsis 4.x
Install Hi-sAFe extension
3. Apply Hi-sAFe modifications
bash
cd /path/to/your/capsis4
patch -p1 < /path/to/simsafe/hisafe/SafeCrop.patch
sh capsis.sh -b safe
See hisafe/README.md for detailed instructions.

4. Install SIMPLACE
Download SIMPLACE 5.x from https://www.simplace.net/downloads

Extract to a directory (e.g., /home/user/SIMPLACE)

5. Install Python dependencies
bash
pip install simplace jpype1
6. Configure paths
Edit python/controllers/multi_cell_agroeco_controller.py:

Python
self.install_dir = "/path/to/SIMPLACE"
self.work_dir = "/path/to/SIMPLACE_WORK"
self.out_dir = "/path/to/SIMPLACE/out"
Edit python/run_hisafe_with_agroeco_multi.py:

Python
capsis_dir = "/path/to/capsis4"
sim_file = "/path/to/your/simulation.sim"
Quick Start
bash
cd simsafe/python
python run_hisafe_with_agroeco_multi.py
See docs/USAGE.md for detailed usage instructions.

Documentation
Installation Guide
Usage Guide
Hi-sAFe Modifications
Detailed Modifications
Requirements
Hi-sAFe: via Capsis 4.x
SIMPLACE: 5.x
Python: 3.8+
simplace
jpype1
Java: 8 (for Hi-sAFe) and 17 (for SIMPLACE)
OS: Linux/Ubuntu (tested on Ubuntu)
