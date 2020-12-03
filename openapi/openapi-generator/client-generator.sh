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
#   KUBERNETES_BRANCH: Kubernetes branch name to get the swagger spec from
#   CLIENT_VERSION: Client version. Will be used in the comment sections of the generated code
#   PACKAGE_NAME: Name of the client package.
#   CLIENT_LANGUAGE: Language of the client. ${CLIENT_LANGUAGE}.xml should exists.
# Optional env vars:
#   OPENAPI_GENERATOR_USER_ORG: openapi-generator-user-org
#   OPENAPI_GENERATOR_COMMIT: openapi-generator-version
# Input vars:
#   $1: output directory
kubeclient::generator::generate_client() {
    : "${CLEANUP_DIRS?Must set CLEANUP_DIRS env var}"
    : "${KUBERNETES_BRANCH?Must set KUBERNETES_BRANCH env var}"
    : "${CLIENT_VERSION?Must set CLIENT_VERSION env var}"
    : "${PACKAGE_NAME?Must set PACKAGE_NAME env var}"
    : "${CLIENT_LANGUAGE?Must set CLIENT_LANGUAGE env var}"

    OPENAPI_GENERATOR_USER_ORG="${OPENAPI_GENERATOR_USER_ORG:-OpenAPITools}"
    OPENAPI_GENERATOR_COMMIT="${OPENAPI_GENERATOR_COMMIT:-v3.3.4}"
    OPENAPI_MODEL_LENGTH="${OPENAPI_MODEL_LENGTH:-}"
    OPENAPI_SKIP_FETCH_SPEC="${OPENAPI_SKIP_FETCH_SPEC:-}"
    OPENAPI_SKIP_BASE_INTERFACE="${OPENAPI_SKIP_BASE_INTERFACE:-}"
    KUBERNETES_CRD_MODE="${KUBERNETES_CRD_MODE:-}"
    KUBERNETES_CRD_GROUP_PREFIX="${KUBERNETES_CRD_GROUP_PREFIX:-}"
    GENERATE_APIS="${GENERATE_APIS:-true}"
    USERNAME="${USERNAME:-kubernetes}"
    REPOSITORY="${REPOSITORY:-kubernetes}"

    local output_dir=$1
    pushd "${output_dir}" > /dev/null
    local output_dir=`pwd`
    popd > /dev/null
    local SCRIPT_ROOT=$(dirname "${BASH_SOURCE}")
    pushd "${SCRIPT_ROOT}" > /dev/null
    local SCRIPT_ROOT=`pwd`
    popd > /dev/null

    mkdir -p "${output_dir}"

    if [ "${USERNAME}" != "kubernetes" ]; then
        image_name="${USERNAME}-${REPOSITORY}-${CLIENT_LANGUAGE}-client-gen-with-openapi-generator:v1"
    else
        image_name="${REPOSITORY}-${CLIENT_LANGUAGE}-client-gen-with-openapi-generator:v1"
    fi

    echo "--- Building docker image ${image_name}..."
    docker build "${SCRIPT_ROOT}"/../ -f "${SCRIPT_ROOT}/Dockerfile" -t "${image_name}" \
        --build-arg OPENAPI_GENERATOR_USER_ORG="${OPENAPI_GENERATOR_USER_ORG}" \
        --build-arg OPENAPI_GENERATOR_COMMIT="${OPENAPI_GENERATOR_COMMIT}" \
        --build-arg GENERATION_XML_FILE="${CLIENT_LANGUAGE}.xml"

    # Docker does not support passing arrays, pass the string representation
    # of the array instead (space separated)
    CLEANUP_DIRS_STRING="${CLEANUP_DIRS[@]}"

    echo "--- Running generator inside container..."
    docker run --security-opt="label=disable" -u $(id -u) \
        -e CLEANUP_DIRS="${CLEANUP_DIRS_STRING}" \
        -e KUBERNETES_BRANCH="${KUBERNETES_BRANCH}" \
        -e CLIENT_VERSION="${CLIENT_VERSION}" \
        -e CLIENT_LANGUAGE="${CLIENT_LANGUAGE}" \
        -e PACKAGE_NAME="${PACKAGE_NAME}" \
        -e OPENAPI_GENERATOR_USER_ORG="${OPENAPI_GENERATOR_USER_ORG}" \
        -e OPENAPI_GENERATOR_COMMIT="${OPENAPI_GENERATOR_COMMIT}" \
        -e OPENAPI_MODEL_LENGTH="${OPENAPI_MODEL_LENGTH}" \
        -e OPENAPI_SKIP_FETCH_SPEC="${OPENAPI_SKIP_FETCH_SPEC}" \
        -e KUBERNETES_CRD_MODE="${KUBERNETES_CRD_MODE}" \
        -e KUBERNETES_CRD_GROUP_PREFIX="${KUBERNETES_CRD_GROUP_PREFIX}" \
        -e GENERATE_APIS="${GENERATE_APIS}" \
        -e OPENAPI_SKIP_BASE_INTERFACE="${OPENAPI_SKIP_BASE_INTERFACE}" \
        -e USERNAME="${USERNAME}" \
        -e REPOSITORY="${REPOSITORY}" \
        -v "${output_dir}:/output_dir" \
        "${image_name}" "/output_dir"

    echo "---Done."
}
