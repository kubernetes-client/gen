#!/usr/bin/env bash

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
    echo "  $(basename ${0}) OUTPUT_DIR SETTING_FILE_PATH"
    echo "    Setting file should define KUBERNETES_BRANCH, CLIENT_VERSION, and PACKAGE_NAME"
    echo "    Setting file can define an optional USERNAME if you're working on a fork"
    echo "    Setting file can define an optional REPOSITORY if you're working on a ecosystem project"
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

source "${SCRIPT_ROOT}/openapi-generator/client-generator.sh"
source "${SETTING_FILE}"

# Latest version as of Mar 15, 2019
OPENAPI_GENERATOR_COMMIT="${OPENAPI_GENERATOR_COMMIT:-c9737cf97d5e31936639842d389118e980ee85a9}"; \
CLIENT_LANGUAGE=haskell-http-client; \
CLEANUP_DIRS=(lib/Kubernetes/OpenAPI/API); \
kubeclient::generator::generate_client "${OUTPUT_DIR}"

CABAL_OVERRIDES=(homepage https://github.com/kubernetes-client/haskell
           author "Auto Generated"
           maintainer "Shimin Guo <smguo2001@gmail.com>"
           license Apache-2.0)

patch_cabal_file() {
    while [[ $# -gt 1 ]]; do
        sed -i 's|^\('$1':[[:space:]]*\).*|\1'"$2"'|' ${OUTPUT_DIR}/*.cabal
        shift 2
    done
}
patch_cabal_file "${CABAL_OVERRIDES[@]}"

# Add license-file after license
sed -i '/^license:/a license-file:   LICENSE' ${OUTPUT_DIR}/*.cabal

ln -sf ../LICENSE ${OUTPUT_DIR}/LICENSE

sed -i '/^copyright:/d' ${OUTPUT_DIR}/*.cabal
echo "---Done."
