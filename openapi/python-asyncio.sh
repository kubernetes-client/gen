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

# Client specific Swagger branch to use.
if [ ${PACKAGE_NAME} == "client" ]; then
    SWAGGER_CODEGEN_COMMIT=f9b2839a3076f26db1b8fc61655a26662f2552ee
else
    SWAGGER_CODEGEN_COMMIT=v2.3.1
fi

# Build the client library in a Docker container.
CLIENT_LANGUAGE=python-asyncio
CLEANUP_DIRS=(client/apis client/models docs test)
kubeclient::generator::generate_client "${OUTPUT_DIR}"

# Generic patches to the generated Python code, most notably renaming the library.
echo "--- Patching generated code..."
find "${OUTPUT_DIR}/test" -type f -name \*.py -exec sed -i "s/\\bclient/${PACKAGE_NAME}.client/g" {} +
find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i "s/\\bclient/${PACKAGE_NAME}.client/g" {} +
find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i "s/${PACKAGE_NAME}.client-python/client-python/g" {} +

# Client specific post-processing of the generated Python wrappers.
if [ ${PACKAGE_NAME} == "client" ]; then
  # workaround https://github.com/swagger-api/swagger-codegen/pull/7905
  find "${OUTPUT_DIR}/client" -type f -name \*.py ! -name '__init__.py' -exec sed -i '/^from .*models.*/d' {} \;

  # workaround https://github.com/swagger-api/swagger-codegen/pull/8204
  # + closing session
  # + support application/strategic-merge-patch+json
  patch "${OUTPUT_DIR}/client/rest.py" "${SCRIPT_ROOT}/python-asyncio-rest.py.patch"

  # workaround https://github.com/swagger-api/swagger-codegen/pull/8401
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/async=/async_req=/g' {} +
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/async bool/async_req bool/g' {} +
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i "s/'async'/'async_req'/g" {} +
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i "s/async parameter/async_req parameter/g" {} +
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i "s/if not async/if not async_req/g" {} +

  # fix imports
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/import client\./import kubernetes_asyncio.client./g' {} +
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/from client/from kubernetes_asyncio.client/g' {} +
  find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/getattr(client\.models/getattr(kubernetes_asyncio.client.models/g' {} +

else
  # Remove circular imports in `v1beta1_json_schema_props.py`.
  sed -i "/^from ${PACKAGE_NAME}\.models.*/d" "${PACKAGE_NAME}/${PACKAGE_NAME}/models/v1beta1_json_schema_props.py"
fi

echo "---Done."
