import subprocess
from typing import Optional, List
from dataclasses import dataclass

from multi_cell_agroeco_controller import MultiCellAgroEcoController, CellWeather

N_CELLS = 25


@dataclass
class CellWeatherBuffer:
    """Buffer to collect weather data for one cell before stepping"""
    cell_rad: Optional[float] = None
    tmin: Optional[float] = None
    tmax: Optional[float] = None
    #vp: Optional[float] = None
    wind: Optional[float] = None
    cell_rain: Optional[float] = None

    def is_complete(self) -> bool:
        """Check if all required weather variables are collected"""
        return all([
            self.cell_rad is not None,
            self.tmin is not None,
            self.tmax is not None,
            #self.vp is not None,
            self.wind is not None,
            self.cell_rain is not None,
        ])

    def to_cell_weather(self) -> CellWeather:
        """Convert to CellWeather dataclass"""
        return CellWeather(
            cell_rad=self.cell_rad,
            tmin=self.tmin,
            tmax=self.tmax,
            #vp=self.vp,
            wind=self.wind,
            cell_rain=self.cell_rain,
        )


def parse_stics_julian_day(line: str) -> int:
    if ":" in line:
        _, rest = line.split(":", 1)
    else:
        rest = line
    tokens = rest.strip().split()
    for t in tokens:
        if t.startswith("sticsJulianDay="):
            return int(t.split("=", 1)[1])
    raise ValueError(f"sticsJulianDay= not found in line: {line}")


def parse_cell_id(line: str) -> int:
    tokens = line.strip().split()
    for t in tokens:
        if t.startswith("cellId="):
            return int(t.split("=", 1)[1])
    raise ValueError(f"cellId= not found in line: {line}")


def parse_value(line: str, key: str) -> Optional[float]:
    """Generic parser for key=value format"""
    tokens = line.strip().split()
    for t in tokens:
        if t.startswith(f"{key}="):
            try:
                return float(t.split("=", 1)[1])
            except ValueError:
                return None
    return None


def run_hisafe_with_agroeco_multi():
    capsis_dir = "/home/hydros/capsis4"
    sim_file = "/home/hydros/mysim/exemple2/exemple.sim"

    cmd = [
        "sh",
        "capsis.sh",
        "-p",
        "script",
        "safe.pgms.ScriptGen",
        sim_file,
    ]

    proc = subprocess.Popen(
        cmd,
        cwd=capsis_dir,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    sim_ctrl: Optional[MultiCellAgroEcoController] = None

    current_stics_day: Optional[int] = None
    # Buffer for collecting weather data per cell
    current_day_weather: List[CellWeatherBuffer] = [CellWeatherBuffer() for _ in range(N_CELLS)]
    current_day_biomass: List[float] = [0.0] * N_CELLS
    simplace_stepped_for_current_day = False

    waiting_for_biomass = False
    last_requested_cell: Optional[int] = None

    try:
        assert proc.stdout is not None
        for raw_line in proc.stdout:
            line = raw_line.rstrip("\n")
            print(line)

            # Initialize SIMPLACE controller on first processGrowth1
            if (
                "DEBUG SafeCrop.processGrowth1:" in line
                and "sticsJulianDay=" in line
                and sim_ctrl is None
            ):
                print(f"[PYTHON] Initializing MultiCellAgroEcoController with {N_CELLS} simulations")
                sim_ctrl = MultiCellAgroEcoController(n_cells=N_CELLS)

            # Parse weather variables from Hi-sAFe output
            # Format: SafeCrop.HiSafeToStics: ... cellRad=2.85 Tmin=-1.221 Tmax=11.97 Vp=7.69 wind=1.04 cellRain=0.0 ... cellId=1
            if "SafeCrop.HiSafeToStics:" in line and "cellId=" in line:
                cell_id = parse_cell_id(line)
                if not (1 <= cell_id <= N_CELLS):
                    continue
                
                cell_idx = cell_id - 1
                
                # Parse each weather variable (note: Hi-sAFe uses Tmin/Tmax/Vp, not tmin/tmax/vp)
                cell_rad = parse_value(line, "cellRad")
                if cell_rad is not None:
                    # Convert MJ/m²/day to J/m²/day
                    current_day_weather[cell_idx].cell_rad = cell_rad * 1_000_000
                
                tmin = parse_value(line, "Tmin")
                if tmin is not None:
                    current_day_weather[cell_idx].tmin = tmin
                
                tmax = parse_value(line, "Tmax")
                if tmax is not None:
                    current_day_weather[cell_idx].tmax = tmax
                
#                vp = parse_value(line, "Vp")
#                if vp is not None:
#                    current_day_weather[cell_idx].vp = vp
                
                wind = parse_value(line, "wind")
                if wind is not None:
                    current_day_weather[cell_idx].wind = wind
                
                cell_rain = parse_value(line, "cellRain")
                if cell_rain is not None:
                    current_day_weather[cell_idx].cell_rain = cell_rain
                
                # Check if all cells have complete weather data
                if not simplace_stepped_for_current_day and all(
                    cell.is_complete() for cell in current_day_weather
                ):
                    if sim_ctrl is None:
                        raise RuntimeError("SIMPLACE controller not initialized")
                    
                    print(
                        f"[PYTHON] All {N_CELLS} weather variables collected for STICS day {current_stics_day}, "
                        f"stepping SIMPLACE now"
                    )
                    
                    # Convert buffers to CellWeather objects
                    weather_data = [cell.to_cell_weather() for cell in current_day_weather]
                    
                    # Step all simulations
                    results = sim_ctrl.step_and_get_biomass(weather_data)
                    
                    # Extract biomass for each cell
                    for idx, res in enumerate(results):
                        current_day_biomass[idx] = res["biomass_t_ha"]
                    
                    print(f"[PYTHON] SIMPLACE stepped: biomass range [{min(current_day_biomass):.4f} - {max(current_day_biomass):.4f}] t/ha")
                    simplace_stepped_for_current_day = True
                
                continue

            # Track STICS Julian day transitions
            if "DEBUG SafeCrop.processGrowth1:" in line and "sticsJulianDay=" in line:
                stics_day = parse_stics_julian_day(line)

                if current_stics_day is None or stics_day > current_stics_day:
                    current_stics_day = stics_day
                    simplace_stepped_for_current_day = False
                    # Reset weather buffers for new day
                    current_day_weather = [CellWeatherBuffer() for _ in range(N_CELLS)]

                continue

            # Handle biomass requests from Hi-sAFe
            if "MANUAL BIOMASS ENTRY REQUEST" in line:
                waiting_for_biomass = True
                last_requested_cell = None
                continue

            if waiting_for_biomass and "Cell ID:" in line:
                parts = line.replace(",", "").split()
                for i, p in enumerate(parts):
                    if p == "ID:" and i + 1 < len(parts):
                        last_requested_cell = int(parts[i + 1])
                        break
                continue

            if waiting_for_biomass and "Enter biomass (t/ha)" in line:
                if sim_ctrl is None:
                    raise RuntimeError("SIMPLACE controller not initialized")
                if last_requested_cell is None:
                    raise RuntimeError("Cell ID not parsed before biomass request")

                cell_index = last_requested_cell - 1
                biomass_to_send = current_day_biomass[cell_index]
                print(
                    f"[PYTHON] Responding for STICS day {current_stics_day}, "
                    f"cell {last_requested_cell} with SIMPLACE biomass={biomass_to_send:.4f} t/ha"
                )

                if proc.stdin is not None:
                    proc.stdin.write(f"{biomass_to_send}\n")
                    proc.stdin.flush()

                waiting_for_biomass = False
                last_requested_cell = None

        proc.wait()
    finally:
        if sim_ctrl is not None:
            sim_ctrl.close()
        if proc.poll() is None:
            proc.terminate()


if __name__ == "__main__":
    run_hisafe_with_agroeco_multi()
