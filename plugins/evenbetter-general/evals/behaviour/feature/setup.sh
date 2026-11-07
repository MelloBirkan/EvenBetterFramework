#!/bin/bash
# The scaffold runs in the empty eval workspace; "$0" is this file's absolute path.
set -euo pipefail
cp -R "$(dirname "$0")/../../_shared/todo-api/." .
