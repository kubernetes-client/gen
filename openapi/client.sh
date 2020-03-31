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

if [ $# -ne 3 ]; then
    echo "Usage:"
    echo "  $(basename ${0}) OUTPUT_DIR SETTING_FILE_PATH CLIENT_LANGUAGE"
    echo "    Setting file should define KUBERNETES_BRANCH, CLIENT_VERSION, and PACKAGE_NAME"
    echo "    Setting file can define an optional USERNAME if you're working on a fork"
    echo "    Setting file can define an optional REPOSITORY if you're working on a ecosystem project"
    exit 1
fi

OUTPUT_DIR=$1
SETTING_FILE=$2
CLIENT_LANGUAGE=${3,,}

case $CLIENT_LANGUAGE in

  c)
    OPENAPI_GENERATOR_COMMIT="${OPENAPI_GENERATOR_COMMIT:-master}"
    CLEANUP_DIRS=(pkg)
    ;;

  csharp)
    CLEANUP_DIRS=(docs src target gradle)
    ;;

  go)
    OPENAPI_GENERATOR_COMMIT="${OPENAPI_GENERATOR_COMMIT:-v3.3.4}"
    CLEANUP_DIRS=(pkg)
    ;;

  haskell)
    OPENAPI_GENERATOR_COMMIT="${OPENAPI_GENERATOR_COMMIT:-a979fd8e13c86431831b0c769ba7b484e744afa5}"
    CLEANUP_DIRS=(lib/Kubernetes/OpenAPI/API)
    ;;

  java)
    CLEANUP_DIRS=(docs src/test/java/io/kubernetes/openapi/apis src/main/java/io/kubernetes/openapi/apis src/main/java/io/kubernetes/openapi/models src/main/java/io/kubernetes/openapi/auth gradle)
    ;;

  perl)
    CLEANUP_DIRS=(docs lib)
    ;;

  python-asyncio)
    CLEANUP_DIRS=(client/apis client/models docs test)
    ;;

  python)
    CLEANUP_DIRS=(client/api client/apis client/models docs test)
    ;;

  ruby)
    CLEANUP_DIRS=(docs lib)
    ;;

  typescript)
    OPENAPI_GENERATOR_COMMIT="${OPENAPI_GENERATOR_COMMIT:-v4.0.3}"
    CLEANUP_DIRS=(api model)
    ;;

  *)
    echo "${CLIENT_LANGUAGE} is not a supported language!"
    ;;
esac

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

kubeclient::generator::generate_client "${OUTPUT_DIR}"

if [[ $CLIENT_LANGUAGE == "csharp" ]]; then
  do
    # hack for generating empty host url
    sed -i '/BaseUri = new System.Uri(\"\");/ d' ${OUTPUT_DIR}/Kubernetes.cs

    # remove public prop from Quantity, (autorest cannot generate empty class)
    sed -i '/JsonProperty/ d' ${OUTPUT_DIR}/Models/ResourceQuantity.cs
    sed -i 's/public string Value/private string Value/' ${OUTPUT_DIR}/Models/ResourceQuantity.cs
    sed -i 's/; set/; private set/' ${OUTPUT_DIR}/Models/V1Patch.cs
  done
fi

if [[ $CLIENT_LANGUAGE == "haskell" ]]; then
  do
    CABAL_OVERRIDES=(homepage https://github.com/kubernetes-client/haskell
               author "Auto Generated"
               maintainer "Shimin Guo <smguo2001@gmail.com>, Akshay Mankar <itsakshaymankar@gmail.com>"
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
    done
fi

if [[ $CLIENT_LANGUAGE == "python-asyncio" ]]; then
  do
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
  done
fi

if [[ $CLIENT_LANGUAGE == "python" ]]; then
  do
    echo "--- Patching generated code..."

    # Post-processing of the generated Python wrapper.
    find "${OUTPUT_DIR}/test" -type f -name \*.py -exec sed -i 's/\bclient/kubernetes.client/g' {} +
    find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i 's/\bclient/kubernetes.client/g' {} +
    find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i 's/kubernetes.client-python/client-python/g' {} +
    find "${OUTPUT_DIR}" -path "${OUTPUT_DIR}/base" -prune -o -type f -a -name \*.md -exec sed -i 's/kubernetes-kubernetes.client/kubernetes-client/g' {} +

    # fix imports
    find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/import client\./import kubernetes.client./g' {} +
    find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/from client/from kubernetes.client/g' {} +
    find "${OUTPUT_DIR}/client/" -type f -name \*.py -exec sed -i 's/getattr(client\.models/getattr(kubernetes.client.models/g' {} +
  done
fi

echo "---Done."
