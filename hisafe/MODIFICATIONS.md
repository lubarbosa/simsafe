# Detailed Modifications to Hi-sAFe

## 1. SafeCrop.java Changes

### File Location
`src/safe/model/SafeCrop.java`

### Change 1: Weather Data Output

**Purpose**: Output cell-specific weather data for SIMPLACE coupling

**Implementation**:
Added a `System.out.println()` statement that outputs:

SafeCrop.HiSafeToStics: HiSFeDay=X SimplaceDay=Y simDate=DD.MM.YYYY cellRad=R Tmin=T1 Tmax=T2 Vp=V wind=W cellRain=P cellId=C

Code

**Variables exported**:
- `cellRad`: Solar radiation (MJ/m²/day) - varies by cell due to tree shading
- `Tmin`: Minimum daily temperature (°C)
- `Tmax`: Maximum daily temperature (°C)
- `Vp`: Vapor pressure (hPa)
- `wind`: Wind speed (m/s)
- `cellRain`: Rainfall (mm) - may vary by cell due to throughfall
- `cellId`: Cell identifier (1-25)

**Execution**: Once per cell per day during growth processing

### Change 2: Manual Biomass Entry

**Purpose**: Allow Python script to override STICS biomass with SIMPLACE values

**Implementation**:
- Prompts: `=== MANUAL BIOMASS ENTRY REQUEST ===`
- Displays: Cell ID and SticsJulianDay
- Waits for stdin input from Python controller
- Accepts: biomass value (t/ha), Enter (keep STICS), or 'q' (quit)

**Execution**: Once per cell per day, after STICS calculation

---

## 2. capsis.sh Changes

### File Location
`capsis.sh` (root directory of Capsis)

### Change: Hardcoded Java 8 Path

**Original code** (line ~105):
```bash
${javaCommand} $jvmOptions $splashoption -Xmx${memo} -cp ./class:./ext/*:$jlp -Djna.library.path=$jlp -Djava.library.path=$jlp capsis.app.Starter $args
Modified code:

bash
#${javaCommand} $jvmOptions $splashoption -Xmx${memo} -cp ./class:./ext/*:$jlp -Djna.library.path=$jlp -Djava.library.path=$jlp capsis.app.Starter $args
/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java $jvmOptions $splashoption -Xmx${memo} -cp ./class:./ext/*:$jlp -Djna.library.path=$jlp -Djava.library.path=$jlp capsis.app.Starter $args
Reason:

Force use of Java 8 for Hi-sAFe (required)
Avoid conflicts when Java 17 is set as system default (needed for SIMPLACE)
⚠️ Warning: This is a system-specific modification. The Java path may differ on other systems.

Alternative approach (more portable): Set JAVA_HOME before running:

bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
sh capsis.sh -p script safe.pgms.ScriptGen test.sim
Summary of Changes
FileLines ChangedTypePortability
SafeCrop.java~2 additionsFeature✅ Portable
capsis.sh1 modificationConfig⚠️ System-specific
Testing the Modifications
Weather output test:

bash
sh capsis.sh -p script safe.pgms.ScriptGen test.sim | grep "SafeCrop.HiSafeToStics"
Biomass input test:

bash
echo "5.0" | sh capsis.sh -p script safe.pgms.ScriptGen test.sim
