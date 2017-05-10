#!/bin/bash

# Copyright 2015 The Kubernetes Authors.
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

# Script to fetch latest swagger spec.
# Puts the updated spec at api/swagger-spec/

set -o errexit
set -o nounset
set -o pipefail

# Generates client.
# Required env vars:
#   CLEANUP_DIRS: List of directories to cleanup before generation for this language
# Input vars:
#   $1: output directory
kubeclient::generator::generate_client() {
    : "${CLEANUP_DIRS?Must set CLEANUP_DIRS env var}"
    : "${KUBERNETES_BRANCH?Must set KUBERNETES_BRANCH env var}"
    : "${CLIENT_VERSION?Must set CLIENT_VERSION env var}"
    : "${PACKAGE_NAME?Must set PACKAGE_NAME env var}"
    : "${CLIENT_LANGUAGE?Must set CLIENT_LANGUAGE env var}"

    local output_dir=$1
    pushd "${output_dir}" > /dev/null
    local output_dir=`pwd`
    popd > /dev/null
    SCRIPT_ROOT=$(dirname "${BASH_SOURCE}")
    pushd "${SCRIPT_ROOT}" > /dev/null
    local SCRIPT_ROOT=`pwd`
    popd > /dev/null

    if ! which mvn > /dev/null 2>&1; then
      echo "Maven is not installed."
      exit
    fi

    mkdir -p "${output_dir}"

    echo "--- Downloading and pre-processing OpenAPI spec"
    python "${SCRIPT_ROOT}/preprocess_spec.py" "${KUBERNETES_BRANCH}" "${output_dir}/swagger.json"

    echo "--- Cleaning up previously generated folders"
    for i in ${CLEANUP_DIRS[@]}; do
        rm -rf "${output_dir}/${i}"
    done

    echo "--- Generating client ..."
    mvn -f "${SCRIPT_ROOT}/${CLIENT_LANGUAGE}.xml" clean generate-sources -Dgenerator.spec.path="${output_dir}/swagger.json" -Dgenerator.output.path="${output_dir}" -D=generator.client.version="${CLIENT_VERSION}" -D=generator.package.name="${PACKAGE_NAME}"

    echo "---Done."
}
