###import simplace
###from typing import List, Dict


###class MultiCellAgroEcoController:
###    """
###    Controller for running multiple AGROECO4CAST_AF simulations in parallel
###    """
###    
###    def __init__(self, n_cells: int = 3):
###        self.install_dir = "/home/hydros/Downloads/SIMPLACE"
###        self.work_dir = "/home/hydros/Downloads/SIMPLACE"
###        self.out_dir = "/home/hydros/Downloads/SIMPLACE/out"
###        self.solution_file = "/home/hydros/Downloads/SIMPLACE/AGROECO4CAST_AF/solution/AF_test.sol.xml"
###        self.n_cells = n_cells
###        self.sh = None
###        
###        self._init_simplace()
###    
###    def _init_simplace(self):
###        """Initialize SIMPLACE and create n_cells simulations"""
###        print(f"[SIMPLACE] Initializing AGROECO4CAST_AF with {self.n_cells} simulations...")
###        
###        self.sh = simplace.initSimplace(self.install_dir, self.work_dir, self.out_dir)
###        simplace.setLogLevel("ERROR")
###        simplace.openProject(self.sh, self.solution_file)
###        
###        # Create n_cells simulations
###        for i in range(1, self.n_cells + 1):
###            simplace.createSimulation(
###                self.sh,
###                {
###                     "projectid": "49662",
###                     "simulationid": "1",
###                     "startdate": "01.01.2020",
###                     "enddate": "02.01.2020",
###                     # Explicitly provide project variables
###                     "vColumn": 452,
###                     "vRow": 294,
###                     "vLocationID": 49662,
###                     "vlat": 52.36479534,
###                     "vlon": 12.41872296,
###                     "vNUTSID": "DE401",
###                     "vSTATE_ID": "DE4",
###                     "vSTATE_NAME": "Brandenburg",
###                }
###            )
###        
###        print(f"[SIMPLACE] Successfully initialized {self.n_cells} simulations\n")
###    
###    def step_and_get_biomass(self) -> List[Dict]:
###        """
###        Step all simulations one day forward and return biomass per cell
###        NO PARAMETERS - uses weather from CSV files
###            
###        Returns:
###            List of dicts with {'cell': int, 'date': str, 'biomass_t_ha': float}
###        """
###        
###        # Step all simulations with filter for outputs we want
###        var_filter = ["CURRENT.DATE", "Biomass.sTAGB"]
###        
###        results = simplace.stepAllSimulations(
###            self.sh,
###            count=1,
###            varFilter=var_filter,
###        )
###        
###        # Extract results per cell
###        cell_results = []
###        for idx, result in enumerate(results):
###            mapped = simplace.varmapToList(result)
###            
###            biomass_g_m2 = float(mapped.get("Biomass.sTAGB", 0.0))
###            biomass_t_ha = biomass_g_m2 * 0.01  # Convert g/m² to t/ha
###            
###            cell_results.append({
###                "cell": idx + 1,
###                "date": mapped.get("CURRENT.DATE", ""),
###                "biomass_t_ha": biomass_t_ha,
###            })
###        
###        return cell_results
###    
###    def close(self):
###        """Close SIMPLACE"""
###        if self.sh:
###            simplace.closeProject(self.sh)
###            print("\n[SIMPLACE] Closed successfully")


#### ============================================================================
#### TEST SCRIPT
#### ============================================================================

###if __name__ == "__main__":
###    print("=" * 60)
###    print("Multi-Cell AGROECO4CAST_AF Controller Test")
###    print("Using weather from CSV files (no override)")
###    print("=" * 60)
###    
###    # Initialize controller with 3 cells
###    ctrl = MultiCellAgroEcoController(n_cells=3)
###    
###    # Simulate 10 days
###    for day in range(1, 2):
###        print(f"\n--- Day {day} ---")
###        
###        # Step and get results (no weather parameters)
###        results = ctrl.step_and_get_biomass()
###        
###        # Print results
###        for res in results:
###            print(f"  Cell {res['cell']}: Date={res['date']}, Biomass={res['biomass_t_ha']:.4f} t/ha")
###    
###    # Close
###    ctrl.close()
###    
###    print("\n" + "=" * 60)
###    print("✓ Test completed successfully!")
###    print("=" * 60)



#!/usr/bin/env python3
"""
Multi-cell AGROECO4CAST_AF controller with Hi-sAFe weather input
"""

import sys
sys.path.append("/home/hydros/.local/lib/python3.8/site-packages")

import simplace
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class CellWeather:
    """Weather data for one cell"""
    cell_rad: float  # J/m²/day
    tmin: float      # °C
    tmax: float      # °C
    #vp: float        # kPa
    wind: float      # m/s
    cell_rain: float # mm


class MultiCellAgroEcoController:
    
    def __init__(self, n_cells: int = 3):
        self.install_dir = "/home/hydros/Downloads/SIMPLACE"
        self.work_dir = "/home/hydros/Downloads/SIMPLACE"
        self.out_dir = "/home/hydros/Downloads/SIMPLACE/out"
        self.solution_file = "/home/hydros/Downloads/SIMPLACE/AGROECO4CAST_AF/solution/AF_test.sol.xml"
        self.n_cells = n_cells
        self.sh = None
        
        self._init_simplace()
    
    def _init_simplace(self):
        """Initialize SIMPLACE and create n_cells simulations"""
        print(f"[SIMPLACE] Initializing AGROECO4CAST_AF with {self.n_cells} simulations...")
        
        self.sh = simplace.initSimplace(self.install_dir, self.work_dir, self.out_dir)
        simplace.setLogLevel("ERROR")
        simplace.openProject(self.sh, self.solution_file)
        
        for i in range(1, self.n_cells + 1):
            simplace.createSimulation(
                self.sh,
                {
                     "projectid": "49662",
                     "simulationid": "1",
                     "startdate": "01.01.2020",
                     "enddate": "02.01.2020",
                     # Explicitly provide project variables
                     "vColumn": 452,
                     "vRow": 294,
                     "vLocationID": 49662,
                     "vlat": 52.36479534,
                     "vlon": 12.41872296,
                     "vNUTSID": "DE401",
                     "vSTATE_ID": "DE4",
                     "vSTATE_NAME": "Brandenburg",
                }
            )
        
        print(f"[SIMPLACE] Successfully initialized {self.n_cells} simulations\n")
    
    def step_and_get_biomass(self, weather_per_cell: List[CellWeather]) -> List[Dict]:
        """
        Step all simulations one day forward with Hi-sAFe weather
        
        Args:
            weather_per_cell: List of CellWeather objects, one per cell
            
        Returns:
            List of dicts with {'cell': int, 'date': str, 'biomass_t_ha': float}
        """
        
        # Build parameter list for each cell
        param_list = []
        for weather in weather_per_cell:
            param_list.append({
                "vCellRad": weather.cell_rad,
                "vTmin": weather.tmin,
                "vTmax": weather.tmax,
                #"vVp": weather.vp,
                "vWind": weather.wind,
                "vCellRain": weather.cell_rain,
            })
        
        # Step all simulations
        var_filter = ["CURRENT.DATE", "Biomass.sTAGB","vCellRad","vTmax","vTmin","vCellRain","vWind"]
        
        results = simplace.stepAllSimulations(
            self.sh,
            count=1,
            parameterlist=param_list,
            varFilter=var_filter,
        )
        
        # Extract results
        cell_results = []
        for idx, result in enumerate(results):
            mapped = simplace.varmapToList(result)
            
            biomass_g_m2 = float(mapped.get("Biomass.sTAGB", 0.0))
            biomass_t_ha = biomass_g_m2 * 0.01
            rad_received = float(mapped.get("vCellRad", 0.0))  # Check what SIMPLACE received
            tmin_received = float(mapped.get("vTmin", 0.0))  # Check what SIMPLACE received
            tmax_received = float(mapped.get("vTmax", 0.0))  # Check what SIMPLACE received
            rain_received = float(mapped.get("vCellRain", 0.0))  # Check what SIMPLACE received
            wind_received = float(mapped.get("vWind", 0.0))  # Check what SIMPLACE received
            #vp_received = float(mapped.get("vVp", 0.0))  # Check what SIMPLACE received
            
            cell_results.append({
                "cell": idx + 1,
                "date": mapped.get("CURRENT.DATE", ""),
                "biomass_t_ha": biomass_t_ha,
                "Radiation":rad_received,
                "TMIN":tmin_received,
                "TMAX":tmax_received,
                "CellRain":rain_received,
                "WIND":wind_received,
                #"VP":vp_received,
            })
        
        return cell_results
    
    def close(self):
        if self.sh:
            simplace.closeProject(self.sh)
            print("\n[SIMPLACE] Closed successfully")


# ============================================================================
# TEST WITH HI-SAFE WEATHER INPUTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Multi-Cell AGROECO4CAST_AF with Hi-sAFe Weather")
    print("=" * 60)
    
    ctrl = MultiCellAgroEcoController(n_cells=3)
    
    for day in range(1, 11):
        print(f"\n--- Day {day} ---")
        
        # Different weather per cell (simulating Hi-sAFe outputs)
        weather_data = [
            CellWeather(
                cell_rad=7_000_000.0 + i * 100_000,
                tmin=5.0 + i * 0.5,
                tmax=20.0 + i * 0.5,
                #vp=1.2 + i * 0.1,
                wind=2.5 + i * 0.2,
                cell_rain=0.0 if day % 3 != 0 else 5.0 + i
            )
            for i in range(3)
        ]
        
        results = ctrl.step_and_get_biomass(weather_data)
        
        for res in results:
            print(f"  Cell {res['cell']}: Date={res['date']}, Biomass={res['biomass_t_ha']:.4f} t/ha, Radiation={res['Radiation']:.0f}, TMIN={res['TMIN']:.1f}, TMAX={res['TMAX']:.1f}, CellRain={res['CellRain']:.1f}, WIND={res['WIND']:.1f}")
            #print(f"  Cell {res['cell']}: Date={res['date']}, Biomass={res['biomass_t_ha']:.4f} t/ha, Radiation={res['rad_received']:.4f}")
    
    ctrl.close()
    
    print("\n" + "=" * 60)
    print("✓ Test completed!")
    print("=" * 60)
