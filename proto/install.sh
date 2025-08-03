#!/bin/bash

# Copyright 2025 The Kubernetes Authors.
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

os_platform=""
release_tag="31.1"
os_architecture="x86_64"

if [[ "${OSTYPE}" == "darwin"* ]]; then
	os_platform="osx"
else
	os_platform="linux"
fi

echo "Installing proto compiler os_platform: ${os_platform}, os_architecture: ${os_architecture}, release_tag: ${release_tag} "

protoc_zip_file="protoc-${release_tag}-${os_platform}-x86_64.zip"

wget "https://github.com/protocolbuffers/protobuf/releases/download/v${release_tag}/${protoc_zip_file}"
unzip "${protoc_zip_file}"
rm "${protoc_zip_file}"
