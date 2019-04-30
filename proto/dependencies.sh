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

mkdir -p k8s.io/api/rbac/v1alpha1
mkdir -p k8s.io/api/rbac/v1
mkdir -p k8s.io/api/rbac/v1beta1
mkdir -p k8s.io/api/networking/v1
mkdir -p k8s.io/api/settings/v1alpha1
mkdir -p k8s.io/api/admissionregistration/v1beta1
mkdir -p k8s.io/api/scheduling/v1alpha1
mkdir -p k8s.io/api/storage/v1
mkdir -p k8s.io/api/storage/v1beta1
mkdir -p k8s.io/api/batch/v2alpha1
mkdir -p k8s.io/api/batch/v1
mkdir -p k8s.io/api/batch/v1beta1
mkdir -p k8s.io/api/apps/v1beta2
mkdir -p k8s.io/api/apps/v1
mkdir -p k8s.io/api/apps/v1beta1
mkdir -p k8s.io/api/authentication/v1
mkdir -p k8s.io/api/authentication/v1beta1
mkdir -p k8s.io/api/admission/v1beta1
mkdir -p k8s.io/api/policy/v1beta1
mkdir -p k8s.io/api/core/v1
mkdir -p k8s.io/api/autoscaling/v1
mkdir -p k8s.io/api/autoscaling/v2beta1
mkdir -p k8s.io/api/autoscaling/v2beta2
mkdir -p k8s.io/api/extensions/v1beta1
mkdir -p k8s.io/api/certificates/v1beta1
mkdir -p k8s.io/api/imagepolicy/v1alpha1
mkdir -p k8s.io/api/authorization/v1
mkdir -p k8s.io/api/authorization/v1beta1
mkdir -p k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1beta1

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

curl -s ${machinery_base}/pkg/runtime/schema/generated.proto \
	> k8s.io/apimachinery/pkg/runtime/schema/generated.proto

# There are currently no release branches for these files.
curl -s ${base}/api/master/rbac/v1alpha1/generated.proto > k8s.io/api/rbac/v1alpha1/generated.proto
curl -s ${base}/api/master/rbac/v1/generated.proto > k8s.io/api/rbac/v1/generated.proto
curl -s ${base}/api/master/rbac/v1beta1/generated.proto > k8s.io/api/rbac/v1beta1/generated.proto
curl -s ${base}/api/master/networking/v1/generated.proto > k8s.io/api/networking/v1/generated.proto
curl -s ${base}/api/master/settings/v1alpha1/generated.proto > k8s.io/api/settings/v1alpha1/generated.proto
curl -s ${base}/api/master/admissionregistration/v1beta1/generated.proto > k8s.io/api/admissionregistration/v1beta1/generated.proto
curl -s ${base}/api/master/scheduling/v1alpha1/generated.proto > k8s.io/api/scheduling/v1alpha1/generated.proto
curl -s ${base}/api/master/storage/v1/generated.proto > k8s.io/api/storage/v1/generated.proto
curl -s ${base}/api/master/storage/v1beta1/generated.proto > k8s.io/api/storage/v1beta1/generated.proto
curl -s ${base}/api/master/batch/v2alpha1/generated.proto > k8s.io/api/batch/v2alpha1/generated.proto
curl -s ${base}/api/master/batch/v1/generated.proto > k8s.io/api/batch/v1/generated.proto
curl -s ${base}/api/master/batch/v1beta1/generated.proto > k8s.io/api/batch/v1beta1/generated.proto
curl -s ${base}/api/master/apps/v1beta2/generated.proto > k8s.io/api/apps/v1beta2/generated.proto
curl -s ${base}/api/master/apps/v1/generated.proto > k8s.io/api/apps/v1/generated.proto
curl -s ${base}/api/master/apps/v1beta1/generated.proto > k8s.io/api/apps/v1beta1/generated.proto
curl -s ${base}/api/master/authentication/v1/generated.proto > k8s.io/api/authentication/v1/generated.proto
curl -s ${base}/api/master/authentication/v1beta1/generated.proto > k8s.io/api/authentication/v1beta1/generated.proto
curl -s ${base}/api/master/admission/v1beta1/generated.proto > k8s.io/api/admission/v1beta1/generated.proto
curl -s ${base}/api/master/policy/v1beta1/generated.proto > k8s.io/api/policy/v1beta1/generated.proto
curl -s ${base}/api/master/core/v1/generated.proto > k8s.io/api/core/v1/generated.proto
curl -s ${base}/api/master/autoscaling/v1/generated.proto > k8s.io/api/autoscaling/v1/generated.proto
curl -s ${base}/api/master/autoscaling/v2beta1/generated.proto > k8s.io/api/autoscaling/v2beta1/generated.proto
curl -s ${base}/api/master/autoscaling/v2beta2/generated.proto > k8s.io/api/autoscaling/v2beta2/generated.proto
curl -s ${base}/api/master/extensions/v1beta1/generated.proto > k8s.io/api/extensions/v1beta1/generated.proto
curl -s ${base}/api/master/certificates/v1beta1/generated.proto > k8s.io/api/certificates/v1beta1/generated.proto
curl -s ${base}/api/master/imagepolicy/v1alpha1/generated.proto > k8s.io/api/imagepolicy/v1alpha1/generated.proto
curl -s ${base}/api/master/authorization/v1/generated.proto > k8s.io/api/authorization/v1/generated.proto
curl -s ${base}/api/master/authorization/v1beta1/generated.proto > k8s.io/api/authorization/v1beta1/generated.proto
curl -s ${base}/apiextensions-apiserver/master/pkg/apis/apiextensions/v1beta1/generated.proto > k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1beta1/generated.proto
