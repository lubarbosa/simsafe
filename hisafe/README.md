# Hi-sAFe Modifications for SimSafe Coupling

This directory contains modifications to Hi-sAFe for coupling with SIMPLACE.

## Modified Files

### 1. SafeCrop.java
**Path**: `src/safe/model/SafeCrop.java`

**Changes**:
- Added `SafeCrop.HiSafeToStics:` output line with cell-specific weather data
  - `cellRad` - Radiation (MJ/m²/day)
  - `Tmin` - Minimum temperature (°C)
  - `Tmax` - Maximum temperature (°C)
  - `Vp` - Vapor pressure (hPa)
  - `wind` - Wind speed (m/s)
  - `cellRain` - Rainfall (mm)
  - `cellId` - Cell identifier (1-25)
- Added manual biomass entry request for Python coupling
  - Prompts for biomass input per cell per day
  - Reads from stdin for bi-directional coupling with SIMPLACE

### 2. capsis.sh
**Path**: `capsis.sh`

**Changes**:
- Hardcoded Java 8 path: `/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java`
- Commented out dynamic `${javaCommand}` variable

**⚠️ Important**: This change is **system-specific**. You will need to modify this path for your system.

## File Structure

## Applying the Modifications

### Prerequisites
- Hi-sAFe installed via Capsis
- Git (for applying patches)
- Java 8 (for Hi-sAFe) and Java 17 (for SIMPLACE)

### Method 1: Apply SafeCrop patch only (recommended)

```bash
cd /path/to/your/capsis4

# Apply ONLY the SafeCrop modifications
patch -p1 < /path/to/simsafe/hisafe/SafeCrop.patch

# Rebuild Hi-sAFe
sh capsis.sh -b safe
Note: Don't apply capsis.patch as it contains a system-specific Java path.

Method 2: Manually edit capsis.sh
If you need to change the Java version:

bash
nano /path/to/capsis4/capsis.sh
Find line ~105 and change:

bash
# Comment out the original line:
#${javaCommand} $jvmOptions $splashoption -Xmx${memo} -cp ./class:./ext/*:$jlp -Djna.library.path=$jlp -Djava.library.path=$jlp capsis.app.Starter $args

# Add your Java 8 path:
/path/to/your/java8/bin/java $jvmOptions $splashoption -Xmx${memo} -cp ./class:./ext/*:$jlp -Djna.library.path=$jlp -Djava.library.path=$jlp capsis.app.Starter $args
Method 3: Copy modified SafeCrop.java directly
bash
# Copy modified SafeCrop.java
cp /path/to/simsafe/hisafe/src/SafeCrop.java /path/to/capsis4/src/safe/model/

# Rebuild Hi-sAFe
cd /path/to/capsis4
sh capsis.sh -b safe
Finding Your Java 8 Path
bash
# Find Java 8 installation
update-alternatives --list java | grep java-8

# Or
ls -la /usr/lib/jvm/ | grep java-8
Verifying the Installation
After applying modifications and rebuilding:

bash
cd /path/to/capsis4
sh capsis.sh -p script safe.pgms.ScriptGen /path/to/test.sim
Look for output lines like:

Code
SafeCrop.HiSafeToStics: HiSFeDay=6 SimplaceDay=6 simDate=06.01.2000 cellRad=2.85 Tmin=-1.221 Tmax=11.97 Vp=7.694376 wind=1.0421159 cellRain=0.0 ... cellId=1
Original Hi-sAFe
Get the original Hi-sAFe from:

Capsis platform: http://capsis.cirad.fr/
Hi-sAFe documentation: https://www1.montpellier.inra.fr/wp-inra/hi-safe/
Version Compatibility
These modifications were developed and tested with:

Hi-sAFe: [Check your version with sh capsis.sh -v]
Capsis: 4.x
Java 8 (for Hi-sAFe)
Java 17 (for SIMPLACE)
Ubuntu/Linux
