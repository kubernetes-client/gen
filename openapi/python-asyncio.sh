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

source "${SCRIPT_ROOT}/client-generator.sh"
source "${SETTING_FILE}"

SWAGGER_CODEGEN_COMMIT=f9b2839a3076f26db1b8fc61655a26662f2552ee; \
CLIENT_LANGUAGE=python-asyncio; \
CLEANUP_DIRS=(client/apis client/models docs test); \
kubeclient::generator::generate_client "${OUTPUT_DIR}"

echo "--- Patching generated code..."
find "${OUTPUT_DIR}/test" -type f -name \*.py -exec sed -i 's/\bclient/kubernetes_asyncio.client/g' {} +
find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i 's/\bclient/kubernetes_asyncio.client/g' {} +
find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i 's/kubernetes_asyncio.client-python/client-python/g' {} +

# workaround https://github.com/swagger-api/swagger-codegen/pull/7905
find "${OUTPUT_DIR}/client" -type f -name \*.py ! -name '__init__.py' -exec sed -i '/^from .*models.*/d' {} \;

# workaround https://github.com/swagger-api/swagger-codegen/pull/8204
# + closing session
# + support application/strategic-merge-patch+json
patch "${OUTPUT_DIR}/client/rest.py" "${SCRIPT_ROOT}/python-asyncio-rest.py.patch"

# fix imports
find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/import client\./import kubernetes_asyncio.client./g' {} +
find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/from client/from kubernetes_asyncio.client/g' {} +
find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/getattr(client\.models/getattr(kubernetes_asyncio.client.models/g' {} +

echo "---Done."
