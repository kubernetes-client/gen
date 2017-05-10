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

# Run this script on the root of the repo to automatically
# detect the language and update its client. Assumptions are:
# - the repo name is the language name.
# - the output folder is named "kubernetes" at the root of the repo
# - setting file is named "settings" at the root of the repo

SCRIPT_ROOT=$(dirname "${BASH_SOURCE}")
pushd "${SCRIPT_ROOT}" > /dev/null
SCRIPT_ROOT=`pwd`
popd > /dev/null

REPO_NAME=$(basename `git rev-parse --show-toplevel`)
REPO_ROOT=$(git rev-parse --show-toplevel)

if [[ ! -f "${SCRIPT_ROOT}/${REPO_NAME}.sh" ]]; then
  echo "Repo name \"${REPO_NAME}\" is not a supported language."
  exit 1
fi

if [[ ! -d "${REPO_ROOT}/kubernetes" ]]; then
  echo "Expected folder named \"kubernetes\" at the root of the repo"
  exit 1
fi

if [[ ! -f "${REPO_ROOT}/settings" ]]; then
  echo "Expected setting file to be at the root of the repo"
  exit 1
fi

echo "Running command \"${SCRIPT_ROOT}/${REPO_NAME}.sh\" \"${REPO_ROOT}/kubernetes\" \"${REPO_ROOT}/settings\""

"${SCRIPT_ROOT}/${REPO_NAME}.sh" "${REPO_ROOT}/kubernetes" "${REPO_ROOT}/settings"


