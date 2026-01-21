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

set -x
curl_cmd="curl --fail -s"

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
mkdir -p k8s.io/api/networking/v1beta1
mkdir -p k8s.io/api/node/v1alpha1
mkdir -p k8s.io/api/node/v1
mkdir -p k8s.io/api/node/v1beta1
mkdir -p k8s.io/api/admissionregistration/v1alpha1
mkdir -p k8s.io/api/admissionregistration/v1
mkdir -p k8s.io/api/admissionregistration/v1beta1
mkdir -p k8s.io/api/scheduling/v1alpha1
mkdir -p k8s.io/api/scheduling/v1
mkdir -p k8s.io/api/scheduling/v1beta1
mkdir -p k8s.io/api/storage/v1alpha1
mkdir -p k8s.io/api/storage/v1
mkdir -p k8s.io/api/storage/v1beta1
mkdir -p k8s.io/api/storagemigration/v1beta1
mkdir -p k8s.io/api/batch/v1
mkdir -p k8s.io/api/batch/v1beta1
mkdir -p k8s.io/api/apidiscovery/v2
mkdir -p k8s.io/api/apidiscovery/v2beta1
mkdir -p k8s.io/api/apiserverinternal/v1alpha1
mkdir -p k8s.io/api/apps/v1beta2
mkdir -p k8s.io/api/apps/v1
mkdir -p k8s.io/api/apps/v1beta1
mkdir -p k8s.io/api/authentication/v1alpha1
mkdir -p k8s.io/api/authentication/v1
mkdir -p k8s.io/api/authentication/v1beta1
mkdir -p k8s.io/api/admission/v1
mkdir -p k8s.io/api/admission/v1beta1
mkdir -p k8s.io/api/policy/v1
mkdir -p k8s.io/api/policy/v1beta1
mkdir -p k8s.io/api/resource/v1alpha3
mkdir -p k8s.io/api/resource/v1
mkdir -p k8s.io/api/resource/v1beta1
mkdir -p k8s.io/api/resource/v1beta2
mkdir -p k8s.io/api/core/v1
mkdir -p k8s.io/api/discovery/v1
mkdir -p k8s.io/api/discovery/v1beta1
mkdir -p k8s.io/api/events/v1
mkdir -p k8s.io/api/events/v1beta1
mkdir -p k8s.io/api/autoscaling/v1
mkdir -p k8s.io/api/autoscaling/v2
mkdir -p k8s.io/api/extensions/v1beta1
mkdir -p k8s.io/api/flowcontrol/v1
mkdir -p k8s.io/api/flowcontrol/v1beta1
mkdir -p k8s.io/api/flowcontrol/v1beta2
mkdir -p k8s.io/api/flowcontrol/v1beta3
mkdir -p k8s.io/api/certificates/v1alpha1
mkdir -p k8s.io/api/certificates/v1
mkdir -p k8s.io/api/certificates/v1beta1
mkdir -p k8s.io/api/coordination/v1alpha2
mkdir -p k8s.io/api/coordination/v1
mkdir -p k8s.io/api/coordination/v1beta1
mkdir -p k8s.io/api/imagepolicy/v1alpha1
mkdir -p k8s.io/api/authorization/v1
mkdir -p k8s.io/api/authorization/v1beta1
mkdir -p k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1beta1
mkdir -p k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1

base=https://raw.githubusercontent.com/kubernetes
machinery_base=${base}/apimachinery/${release}
$curl_cmd ${machinery_base}/pkg/api/resource/generated.proto \
	> k8s.io/apimachinery/pkg/api/resource/generated.proto

$curl_cmd ${machinery_base}/pkg/apis/meta/v1/generated.proto \
	> k8s.io/apimachinery/pkg/apis/meta/v1/generated.proto

$curl_cmd ${machinery_base}/pkg/util/intstr/generated.proto \
	> k8s.io/apimachinery/pkg/util/intstr/generated.proto

$curl_cmd ${machinery_base}/pkg/runtime/generated.proto \
	> k8s.io/apimachinery/pkg/runtime/generated.proto

$curl_cmd ${machinery_base}/pkg/runtime/schema/generated.proto \
	> k8s.io/apimachinery/pkg/runtime/schema/generated.proto

# There are currently no release branches for these files.
$curl_cmd ${base}/api/master/rbac/v1alpha1/generated.proto > k8s.io/api/rbac/v1alpha1/generated.proto
$curl_cmd ${base}/api/master/rbac/v1/generated.proto > k8s.io/api/rbac/v1/generated.proto
$curl_cmd ${base}/api/master/rbac/v1beta1/generated.proto > k8s.io/api/rbac/v1beta1/generated.proto
$curl_cmd ${base}/api/master/networking/v1/generated.proto > k8s.io/api/networking/v1/generated.proto
$curl_cmd ${base}/api/master/networking/v1beta1/generated.proto > k8s.io/api/networking/v1beta1/generated.proto
$curl_cmd ${base}/api/master/node/v1alpha1/generated.proto > k8s.io/api/node/v1alpha1/generated.proto
$curl_cmd ${base}/api/master/node/v1/generated.proto > k8s.io/api/node/v1/generated.proto
$curl_cmd ${base}/api/master/node/v1beta1/generated.proto > k8s.io/api/node/v1beta1/generated.proto
$curl_cmd ${base}/api/master/admissionregistration/v1alpha1/generated.proto > k8s.io/api/admissionregistration/v1alpha1/generated.proto
$curl_cmd ${base}/api/master/admissionregistration/v1beta1/generated.proto > k8s.io/api/admissionregistration/v1beta1/generated.proto
$curl_cmd ${base}/api/master/admissionregistration/v1/generated.proto > k8s.io/api/admissionregistration/v1/generated.proto
$curl_cmd ${base}/api/master/apidiscovery/v2/generated.proto > k8s.io/api/apidiscovery/v2/generated.proto
$curl_cmd ${base}/api/master/apidiscovery/v2beta1/generated.proto > k8s.io/api/apidiscovery/v2beta1/generated.proto
$curl_cmd ${base}/api/master/apiserverinternal/v1alpha1/generated.proto > k8s.io/api/apiserverinternal/v1alpha1/generated.proto
$curl_cmd ${base}/api/master/scheduling/v1alpha1/generated.proto > k8s.io/api/scheduling/v1alpha1/generated.proto
$curl_cmd ${base}/api/master/scheduling/v1/generated.proto > k8s.io/api/scheduling/v1/generated.proto
$curl_cmd ${base}/api/master/scheduling/v1beta1/generated.proto > k8s.io/api/scheduling/v1beta1/generated.proto
$curl_cmd ${base}/api/master/storage/v1/generated.proto > k8s.io/api/storage/v1/generated.proto
$curl_cmd ${base}/api/master/storage/v1alpha1/generated.proto > k8s.io/api/storage/v1alpha1/generated.proto
$curl_cmd ${base}/api/master/storage/v1beta1/generated.proto > k8s.io/api/storage/v1beta1/generated.proto
$curl_cmd ${base}/api/master/storagemigration/v1beta1/generated.proto > k8s.io/api/storagemigration/v1beta1/generated.proto
$curl_cmd ${base}/api/master/batch/v1/generated.proto > k8s.io/api/batch/v1/generated.proto
$curl_cmd ${base}/api/master/batch/v1beta1/generated.proto > k8s.io/api/batch/v1beta1/generated.proto
$curl_cmd ${base}/api/master/apps/v1beta2/generated.proto > k8s.io/api/apps/v1beta2/generated.proto
$curl_cmd ${base}/api/master/apps/v1/generated.proto > k8s.io/api/apps/v1/generated.proto
$curl_cmd ${base}/api/master/apps/v1beta1/generated.proto > k8s.io/api/apps/v1beta1/generated.proto
$curl_cmd ${base}/api/master/authentication/v1alpha1/generated.proto > k8s.io/api/authentication/v1alpha1/generated.proto
$curl_cmd ${base}/api/master/authentication/v1/generated.proto > k8s.io/api/authentication/v1/generated.proto
$curl_cmd ${base}/api/master/authentication/v1beta1/generated.proto > k8s.io/api/authentication/v1beta1/generated.proto
$curl_cmd ${base}/api/master/admission/v1beta1/generated.proto > k8s.io/api/admission/v1beta1/generated.proto
$curl_cmd ${base}/api/master/admission/v1/generated.proto > k8s.io/api/admission/v1/generated.proto
$curl_cmd ${base}/api/master/policy/v1/generated.proto > k8s.io/api/policy/v1/generated.proto
$curl_cmd ${base}/api/master/policy/v1beta1/generated.proto > k8s.io/api/policy/v1beta1/generated.proto
$curl_cmd ${base}/api/master/resource/v1alpha3/generated.proto > k8s.io/api/resource/v1alpha3/generated.proto
$curl_cmd ${base}/api/master/resource/v1/generated.proto > k8s.io/api/resource/v1/generated.proto
$curl_cmd ${base}/api/master/resource/v1beta1/generated.proto > k8s.io/api/resource/v1beta1/generated.proto
$curl_cmd ${base}/api/master/resource/v1beta2/generated.proto > k8s.io/api/resource/v1beta2/generated.proto
$curl_cmd ${base}/api/master/core/v1/generated.proto > k8s.io/api/core/v1/generated.proto
$curl_cmd ${base}/api/master/discovery/v1/generated.proto > k8s.io/api/discovery/v1/generated.proto
$curl_cmd ${base}/api/master/discovery/v1beta1/generated.proto > k8s.io/api/discovery/v1beta1/generated.proto
$curl_cmd ${base}/api/master/events/v1/generated.proto > k8s.io/api/events/v1/generated.proto
$curl_cmd ${base}/api/master/events/v1beta1/generated.proto > k8s.io/api/events/v1beta1/generated.proto
$curl_cmd ${base}/api/master/autoscaling/v1/generated.proto > k8s.io/api/autoscaling/v1/generated.proto
$curl_cmd ${base}/api/master/autoscaling/v2/generated.proto > k8s.io/api/autoscaling/v2/generated.proto
$curl_cmd ${base}/api/master/extensions/v1beta1/generated.proto > k8s.io/api/extensions/v1beta1/generated.proto
$curl_cmd ${base}/api/master/flowcontrol/v1/generated.proto > k8s.io/api/flowcontrol/v1/generated.proto
$curl_cmd ${base}/api/master/flowcontrol/v1beta1/generated.proto > k8s.io/api/flowcontrol/v1beta1/generated.proto
$curl_cmd ${base}/api/master/flowcontrol/v1beta2/generated.proto > k8s.io/api/flowcontrol/v1beta2/generated.proto
$curl_cmd ${base}/api/master/flowcontrol/v1beta3/generated.proto > k8s.io/api/flowcontrol/v1beta3/generated.proto
$curl_cmd ${base}/api/master/certificates/v1alpha1/generated.proto > k8s.io/api/certificates/v1alpha1/generated.proto
$curl_cmd ${base}/api/master/certificates/v1/generated.proto > k8s.io/api/certificates/v1/generated.proto
$curl_cmd ${base}/api/master/certificates/v1beta1/generated.proto > k8s.io/api/certificates/v1beta1/generated.proto
$curl_cmd ${base}/api/master/coordination/v1alpha2/generated.proto > k8s.io/api/coordination/v1alpha2/generated.proto
$curl_cmd ${base}/api/master/coordination/v1/generated.proto > k8s.io/api/coordination/v1/generated.proto
$curl_cmd ${base}/api/master/coordination/v1beta1/generated.proto > k8s.io/api/coordination/v1beta1/generated.proto
$curl_cmd ${base}/api/master/imagepolicy/v1alpha1/generated.proto > k8s.io/api/imagepolicy/v1alpha1/generated.proto
$curl_cmd ${base}/api/master/authorization/v1/generated.proto > k8s.io/api/authorization/v1/generated.proto
$curl_cmd ${base}/api/master/authorization/v1beta1/generated.proto > k8s.io/api/authorization/v1beta1/generated.proto
$curl_cmd ${base}/apiextensions-apiserver/master/pkg/apis/apiextensions/v1beta1/generated.proto > k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1beta1/generated.proto
$curl_cmd ${base}/apiextensions-apiserver/master/pkg/apis/apiextensions/v1/generated.proto > k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1/generated.proto
