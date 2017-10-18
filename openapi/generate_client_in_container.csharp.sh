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

# Script to fetch latest swagger spec.
# Puts the updated spec at api/swagger-spec/

set -o errexit
set -o nounset
set -o pipefail

# Generates client.
# Required env vars:
#   CLEANUP_DIRS: List of directories (string separated by space) to cleanup before generation for this language
#   KUBERNETES_BRANCH: Kubernetes branch name to get the swagger spec from
#   CLIENT_VERSION: Client version. Will be used in the comment sections of the generated code
#   PACKAGE_NAME: Name of the client package.
# Input vars:
#   $1: output directory
: "${CLEANUP_DIRS?Must set CLEANUP_DIRS env var}"
: "${KUBERNETES_BRANCH?Must set KUBERNETES_BRANCH env var}"
: "${CLIENT_VERSION?Must set CLIENT_VERSION env var}"
: "${PACKAGE_NAME?Must set PACKAGE_NAME env var}"

output_dir=$1
pushd "${output_dir}" > /dev/null
output_dir=`pwd`
popd > /dev/null
SCRIPT_ROOT=$(dirname "${BASH_SOURCE}")
pushd "${SCRIPT_ROOT}" > /dev/null
SCRIPT_ROOT=`pwd`
popd > /dev/null


mkdir -p "${output_dir}"

echo "--- Downloading and pre-processing OpenAPI spec"
python "${SCRIPT_ROOT}/preprocess_spec.py" "${KUBERNETES_BRANCH}" "${output_dir}/swagger.json"

echo "--- Cleaning up previously generated folders"
for i in ${CLEANUP_DIRS}; do
    echo "--- Cleaning up ${output_dir}/${i}"
    rm -rf "${output_dir}/${i}"
done

echo "--- Generating client ..."
# TODO new wayautorest --input-file "${output_dir}/swagger.json" --namespace "${PACKAGE_NAME}" --output-folder "${output_dir}" --add-credentials
autorest -Input "${output_dir}/swagger.json" -CodeGenerator CSharp -Namespace "${PACKAGE_NAME}" -PackageVersion "${CLIENT_VERSION}"  -OutputDirectory "${output_dir}" -AddCredentials true

mkdir -p "${output_dir}/.autorest-codegen"
autorest --info --json > "${output_dir}/.autorest-codegen/autorest-info.json"

echo "---Done."
