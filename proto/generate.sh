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

# usage: generate.sh $LANGUAGE $OUTPUT_DIR
#  current tested languages:
#   * java

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if ! which protoc > /dev/null; then
  ${dir}/install.sh
  proto=./bin/protoc
else
  proto=$(which protoc)
fi

${dir}/dependencies.sh

# The format here is <file-name>;<generated-class-name>
files="v1.proto;V1 \
       k8s.io/apimachinery/pkg/api/resource/generated.proto;Resource \
       k8s.io/apimachinery/pkg/apis/meta/v1/generated.proto;Meta \
       k8s.io/apimachinery/pkg/runtime/generated.proto;Runtime \
       k8s.io/apimachinery/pkg/runtime/schema/generated.proto;RuntimeSchema \
       k8s.io/apimachinery/pkg/util/intstr/generated.proto;IntStr"

proto_files=""

echo 'Munging proto file packages'

# This is a little hacky, but we know the go_package directive is in the
# right place, so add a marker, and then append more package declarations.
# Sorry, I like perl.
for info in ${files}; do
  file=$(echo ${info} | cut -d ";" -f 1)
  class=$(echo ${info} | cut -d ";" -f 2)
  proto_files="${file} ${proto_files}"
  perl -pi -e \
    's/option go_package = "(.*)";/option go_package = "$1";\n\/\/ PKG/' \
    ${file} 
  perl -pi -e \
    's/\/\/ PKG/\/\/ PKG\noption java_package = "io.kubernetes.client.proto";/' \
    ${file}
  perl -pi -e \
    "s/\/\/ PKG/\/\/ PKG\noption java_outer_classname = \"${class}\";/" \
    ${file}
  
  # Other package declarations can go here.
done

echo "Generating code for $1"
${proto} -I${dir} ${proto_files} --${1}_out=${2}
