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

release=${1:-"master"}

echo Downloading proto files for ${release}

mkdir -p k8s.io/apimachinery/pkg/api/resource
mkdir -p k8s.io/apimachinery/pkg/apis/meta/v1
mkdir -p k8s.io/apimachinery/pkg/util/intstr
mkdir -p k8s.io/apimachinery/pkg/runtime/schema
mkdir -p k8s.io/apis/meta/v1

base=https://raw.githubusercontent.com/kubernetes
machinery_base=${base}/apimachinery/${release}
curl -s ${machinery_base}/pkg/api/resource/generated.proto \
	> k8s.io/apimachinery/pkg/api/resource/generated.proto

curl -s ${machinery_base}/pkg/apis/meta/v1/generated.proto \
	> k8s.io/apimachinery/pkg/apis/meta/v1/generated.proto

curl -s ${machinery_base}/pkg/util/intstr/generated.proto \
	> k8s.io/apimachinery/pkg/util/intstr/generated.proto

curl -s ${machinery_base}/pkg/runtime/generated.proto \
	> k8s.io/apimachinery/pkg/runtime/generated.proto

curl -s ${machinery_base}/runtime/schema/generated.proto \
	> k8s.io/apimachinery/pkg/runtime/schema/generated.proto

# There are currently no release branches for this file.
curl -s ${base}/api/master/core/v1/generated.proto > v1.proto
