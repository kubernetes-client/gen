#!/bin/bash

# Copyright 2017 The Kubernetes Authors.
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
    echo "    python.sh OUTPUT_DIR SETTING_FILE_PATH"
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

# SWAGGER_CODEGEN_COMMIT=d2b91073e1fc499fea67141ff4c17740d25f8e83; \
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
echo '21a22,23
> import asyncio
> 
81a84,86
>     def __del__(self):
>         asyncio.ensure_future(self.pool_manager.close())
> 
130a136,138
>                 if headers['Content-Type'] == 'application/json-patch+json':
>                     if not isinstance(body, list):
>                         headers['Content-Type'] = 'application/strategic-merge-patch+json'
164c172,174
<         async with self.pool_manager.request(**args) as r:
---
>         r = await self.pool_manager.request(**args)
>         if _preload_content:
> 
168,169c178,179
<         # log response body
<         logger.debug("response body: %s", r.data)
---
>             # log response body
>             logger.debug("response body: %s", r.data)
171,172c181,182
<         if not 200 <= r.status <= 299:
<             raise ApiException(http_resp=r)
---
>             if not 200 <= r.status <= 299:
>                 raise ApiException(http_resp=r)' | patch "${OUTPUT_DIR}/client/rest.py"

# fix imports
find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/import client\./import kubernetes_asyncio.client./g' {} +
find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/from client/from kubernetes_asyncio.client/g' {} +
find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/getattr(client\.models/getattr(kubernetes_asyncio.client.models/g' {} +

echo "---Done."
