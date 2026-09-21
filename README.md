<p align="center">
  <img src="docs/assets/simsafe-logo.svg" alt="SimSafe logo showing a stylized tree above a field grid to represent agroforestry simulation coupling" width="180">
</p>

<h1 align="center">SimSafe</h1>

<p align="center"><strong>SIMPLACE–Hi-sAFe Integrated AgroForestry Simulation Environment</strong></p>

<p align="center">Couples Hi-sAFe agroforestry outputs with SIMPLACE / AGROECO4CAST_AF crop simulations and returns biomass feedback to Hi-sAFe.</p>

> [!IMPORTANT]
> This repository contains the coupling code, patches, and configuration scaffolding. It does **not** bundle the external Hi-sAFe/Capsis or SIMPLACE binary distributions, and using those tools may require separate installation, licensing acceptance, and version checks in your own environment.

## Overview

At a high level, SimSafe orchestrates a daily feedback loop:

1. **Hi-sAFe (Capsis)** runs the agroforestry simulation and emits per-cell weather values.
2. **Python coupling code** reads those values from Hi-sAFe output.
3. **SIMPLACE / AGROECO4CAST_AF** runs one crop simulation per cell using the imported daily weather.
4. **Python** collects the resulting biomass values.
5. **Hi-sAFe** prompts for biomass input, and the Python runner sends the SIMPLACE biomass back through standard input.

```text
Hi-sAFe (Capsis)
    │  cellRad, Tmin, Tmax, wind, cellRain, cellId
    ▼
Python runner (`python/run_hisafe_with_agroeco_multi.py`)
    │  builds per-cell weather payloads
    ▼
SIMPLACE / AGROECO4CAST_AF
    │  one simulation handle per cell
    ▼
Python controller (`python/controllers/multi_cell_agroeco_controller.py`)
    │  biomass_t_ha per cell
    ▼
Hi-sAFe stdin biomass feedback
```

For the Hi-sAFe-side patch details and coupling behavior, see [`hisafe/README.md`](hisafe/README.md).

## Repository layout

The main repository contents are:

| Path | Purpose |
| --- | --- |
| [`README.md`](README.md) | Project landing page and setup notes |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history for the repository |
| [`VERSION`](VERSION) | Current project version |
| [`hisafe/`](hisafe/) | Hi-sAFe patch files, modified sources, and patching notes |
| [`python/`](python/) | Python runner and SIMPLACE controller code |
| [`scripts/`](scripts/) | Helper shell scripts, including Java runtime setup |
| [`simplace/`](simplace/) | SIMPLACE solution/project material tracked in this repository |

## Prerequisites and environment notes

SimSafe depends on software that is maintained outside this repository:

- **Hi-sAFe on Capsis**: required for the agroforestry side of the coupling.
- **SIMPLACE 5.x**: required for the crop simulation side.
- **Python 3** with the Python packages used by the coupling scripts.
- **Java runtimes**: the repository documentation and helper scripts indicate a split setup where:
  - **Java 8** is used for Hi-sAFe/Capsis-related execution.
  - **Java 17** is used for SIMPLACE-related execution.

This Java split is documented by the tracked files in this repository (for example, the patched Hi-sAFe launcher notes and the Java 17 helper script in `scripts/`). Treat it as a **repository-specific integration pattern**, not a universal guarantee for every Hi-sAFe or SIMPLACE installation. Adjust paths and versions to match your system and the external software versions you install.

## Installation and setup

### 1. Clone this repository

```bash
git clone https://github.com/lubarbosa/simsafe.git
cd simsafe
```

### 2. Install external prerequisites

Install or obtain access to:

- a **Capsis/Hi-sAFe** installation compatible with the patching approach described in [`hisafe/README.md`](hisafe/README.md)
- a **SIMPLACE 5.x** installation that includes the components required by the tracked AGROECO4CAST_AF solution files

Because these distributions are external to this repository, confirm their installation steps, licensing terms, and version compatibility from their original sources before continuing.

### 3. Apply the Hi-sAFe patch

The repository includes patch files under [`hisafe/`](hisafe/). The Hi-sAFe README recommends applying the `SafeCrop` changes separately because the tracked `capsis.sh` modification is system-specific.

```bash
cd /path/to/your/capsis4
patch -p1 < /path/to/simsafe/hisafe/SafeCrop.patch
sh capsis.sh -b safe
```

If you also adapt `capsis.sh`, review the warnings in [`hisafe/README.md`](hisafe/README.md) first: the tracked example hard-codes a Java 8 path and will likely need to be edited for your machine.

### 4. Install Python dependencies

The repository code imports `simplace` and `jpype1`.

```bash
python3 -m pip install simplace jpype1
```

### 5. Configure repository-specific paths

Before running the coupled workflow, update the hard-coded paths in the tracked Python entry points to match your installation:

- In [`python/controllers/multi_cell_agroeco_controller.py`](python/controllers/multi_cell_agroeco_controller.py), review:
  - `install_dir`
  - `work_dir`
  - `out_dir`
  - `solution_file`
- In [`python/run_hisafe_with_agroeco_multi.py`](python/run_hisafe_with_agroeco_multi.py), review:
  - `capsis_dir`
  - `sim_file`

These values currently point to local machine paths used during development and are expected to be customized in downstream environments.

### 6. Optional Java runtime helper

The repository includes [`scripts/multi_cell_agroeco_controller_java17.sh`](scripts/multi_cell_agroeco_controller_java17.sh), which exports a Java 17 runtime before launching the Python controller. Treat it as an example helper script and verify its paths before using it.

## Quick start

After installing the external dependencies, applying the Hi-sAFe patch, and updating the local paths:

```bash
cd python
PYTHONPATH=controllers python3 run_hisafe_with_agroeco_multi.py
```

This launches the Python bridge that:

- starts the Hi-sAFe script runner from `capsis_dir`
- waits for `SafeCrop.HiSafeToStics` lines
- aggregates weather for all configured cells
- steps SIMPLACE
- writes biomass responses back to Hi-sAFe through stdin

## Troubleshooting and known limitations

- **External binaries are required**: the repository alone is not enough to execute the full workflow.
- **Version compatibility is environment-dependent**: if Hi-sAFe/Capsis or SIMPLACE interfaces differ from the versions used when this repository was assembled, patch application or runtime behavior may need adjustment.
- **Java compatibility can be split across tools**: the tracked files indicate Java 8 for Hi-sAFe/Capsis and Java 17 for SIMPLACE. Misaligned Java environments are a likely source of startup failures.
- **`capsis.sh` is system-specific**: the patched launcher example in `hisafe/` hard-codes a Java path and should be reviewed rather than copied blindly.
- **Biomass feedback uses interactive stdin/stdout coupling**: the Python runner watches for Hi-sAFe prompts and responds interactively. If stdout format changes, buffering changes, or prompts are localized differently, the coupling may break.
- **Repository paths are not auto-discovered**: the Python controller and runner currently rely on explicit filesystem paths that must be edited for each setup.

## Development and contribution

If you plan to extend the coupling:

1. Review [`hisafe/README.md`](hisafe/README.md) and [`hisafe/MODIFICATIONS.md`](hisafe/MODIFICATIONS.md) before editing patch files.
2. Keep Python-side changes aligned with the weather keys and biomass prompt flow used by the patched Hi-sAFe code.
3. Prefer updating this README when setup assumptions or required paths change.
4. Validate documentation examples against the tracked repository structure before publishing them.

## Documentation map

- [`CHANGELOG.md`](CHANGELOG.md) — repository release notes
- [`hisafe/README.md`](hisafe/README.md) — Hi-sAFe patch overview and application notes
- [`hisafe/MODIFICATIONS.md`](hisafe/MODIFICATIONS.md) — detailed description of the tracked Hi-sAFe changes
- [`python/`](python/) — Python orchestration code for the coupling workflow
- [`scripts/`](scripts/) — helper shell scripts
- [`simplace/`](simplace/) — tracked SIMPLACE solution/project files

## Citation

No formal citation text is currently provided in this repository. If you publish work based on SimSafe, consider citing the associated software components and adding project-specific citation guidance in a future update.

## License

No `LICENSE` file is currently present in the repository root. Until a license is added by the maintainers, treat reuse and redistribution as undefined and verify the status with the repository owner.
