#!/bin/bash

# Copyright 2018 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -o errexit
set -o nounset
set -o pipefail

ARGC=$#

if [ $# -ne 2 ]; then
    echo "Usage:"
    echo "    python-asyncio.sh OUTPUT_DIR SETTING_FILE_PATH"
    echo "    Setting file should define KUBERNETES_BRANCH, CLIENT_VERSION, and PACKAGE_NAME"
    exit 1
fi


OUTPUT_DIR=$1
SETTING_FILE=$2
mkdir -p "${OUTPUT_DIR}"

SCRIPT_ROOT=$(dirname "${BASH_SOURCE}")
pushd "${SCRIPT_ROOT}" > /dev/null
SCRIPT_ROOT=`pwd`
popd > /dev/null

pushd "${OUTPUT_DIR}" > /dev/null
OUTPUT_DIR=`pwd`
popd > /dev/null

source "${SETTING_FILE}"

# use openapi-generator to generate library
source "${SCRIPT_ROOT}/openapi-generator/client-generator.sh"
OPENAPI_GENERATOR_COMMIT="${OPENAPI_GENERATOR_COMMIT:-v6.6.0}"

CLIENT_LANGUAGE=python-asyncio
CLEANUP_DIRS=(client/apis client/models docs test)
kubeclient::generator::generate_client "${OUTPUT_DIR}"

# Generic patches to the generated Python code, most notably renaming the library.
echo "--- Patching generated code..."

if [ ${PACKAGE_NAME} == "client" ]; then

  # Post-processing of the generated Python wrapper.
  find "${OUTPUT_DIR}/test" -type f -name \*.py -exec sed -i 's/\bclient/kubernetes_asyncio.client/g' {} +
  find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i 's/\bclient/kubernetes_asyncio.client/g' {} +
  find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i 's/kubernetes_asyncio.client-python/client-python/g' {} +

  # fix imports
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/import client\./import kubernetes_asyncio.client./g' {} +
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/from client/from kubernetes_asyncio.client/g' {} +
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/getattr(client\.models/getattr(kubernetes_asyncio.client.models/g' {} +

else

  # Post-processing of the generated Python wrapper.
  find "${OUTPUT_DIR}/test" -type f -name \*.py -exec sed -i "s/\\bclient/${PACKAGE_NAME}.client/g" {} +
  find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i "s/\\bclient/${PACKAGE_NAME}.client/g" {} +
  find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i "s/${PACKAGE_NAME}.client-python/client-python/g" {} +

fi

echo "---Done."
