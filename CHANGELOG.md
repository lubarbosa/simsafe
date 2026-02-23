# Changelog

All notable changes to SimSafe will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2026-02-23

### Added
- Initial release of SimSafe coupling framework
- Multi-cell SIMPLACE controller for AGROECO4CAST_AF
- Hi-sAFe integration with cell-specific weather data
- Support for 25 independent crop simulations
- Bidirectional coupling: Hi-sAFe → SIMPLACE → Hi-sAFe
- Python controllers for automated simulation workflow
- Documentation for installation and usage

### Features
- Real-time weather data passing (radiation, temperature, vapor pressure, wind, rain)
- Per-cell biomass feedback to Hi-sAFe
- Daily timestep synchronization
- Configurable number of cells

### Hi-sAFe Modifications
- Modified `SafeCrop.java` to output cell-specific weather
- Added manual biomass entry mechanism
- Modified `capsis.sh` for Java 8 compatibility

### SIMPLACE Components
- AGROECO4CAST_AF solution adapted for multi-cell simulations
- Per-cell weather variable handling
- Shell script for Java 17 compatibility

