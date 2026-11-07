# Shared scaffold helpers. A case's setup.sh sources this file with
#   . "$(dirname "$0")/../../_shared/scaffold.sh"
# The scaffold runs in the empty eval workspace, and "$0" is the absolute path of
# the case's setup.sh, so the fixture is read from here rather than copied per case.
set -euo pipefail
EB_SHARED="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy the PlantCare app (five Swift files with planted HIG and accessibility issues).
plantcare_fixture() {
  cp -R "$EB_SHARED/plantcare/PlantCare" ./PlantCare
}

# Render a seed audit report at .evenbetter/plant-care/ with the plugin's report helper.
# $1 is analyzed (with two planted false positives) or validated.
plantcare_report() {
  python3 "$EB_SHARED/seed_report.py" "$1" "$PWD"
}
