#!/usr/bin/env bash

PACKAGE_NAME=${PACKAGE_NAME:-client}
CLIENT_VERSION=${CLIENT_VERSION:-17.0.0-snapshot}
GENERATE_APIS=${GENERATE_APIS:-false}
OUTPUT_DIR=${OUTPUT_DIR:-python}
OPENAPI_MODEL_LENGTH=${OPENAPI_MODEL_LENGTH:-}
HIDE_GENERATION_TIMESTAMP=${HIDE_GENERATION_TIMESTAMP:-false}
OPENAPI_SKIP_BASE_INTERFACE=
KUBERNETES_CRD_GROUP_PREFIX=

print_usage() {
  echo "Usage: generate a python project using input openapi spec from stdin" >& 2
  echo " -c: project version of the generated python project." >& 2
  echo " -n: the prefix of the target CRD's api group to generate." >& 2
  echo " -g: generate crd apis." >& 2
  echo " -p: the base package name of the generated python project. " >& 2
  echo " -o: output directory of the generated python project. " >& 2
  echo " -l: keep the n last segments for the generated class name. " >& 2
  echo " -h: hide generation timestamp" >& 2
}

while getopts 'c:g:h:n:l:p:o:' flag; do
  case "${flag}" in
    c) CLIENT_VERSION="${OPTARG}" ;;
    g) GENERATE_APIS="${OPTARG}" ;;
    h) HIDE_GENERATION_TIMESTAMP="${OPTARG}" ;;
    n) KUBERNETES_CRD_GROUP_PREFIX="${OPTARG}" ;;
    l) OPENAPI_MODEL_LENGTH="${OPTARG}" ;;
    p) PACKAGE_NAME="${OPTARG}" ;;
    o) OUTPUT_DIR="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

echo "KUBERNETES_CRD_GROUP_PREFIX: $KUBERNETES_CRD_GROUP_PREFIX" >& 2
echo "OPENAPI_MODEL_LENGTH: $OPENAPI_MODEL_LENGTH" >& 2
echo "PACKAGE_NAME: $PACKAGE_NAME" >& 2
echo "GENERATE_APIS: $GENERATE_APIS" >& 2
echo "CLIENT_VERSION: $CLIENT_VERSION" >& 2
echo "OUTPUT_DIR: $OUTPUT_DIR" >& 2
echo "HIDE_GENERATION_TIMESTAMP: $HIDE_GENERATION_TIMESTAMP" >& 2
echo "" >& 2 # empty line


mkdir -p "${OUTPUT_DIR}"

echo 'rendering settings file to /tmp/settings' >& 2
read -d '' settings << EOF
export KUBERNETES_BRANCH="${KUBERNETES_BRANCH}"
export CLIENT_VERSION="${CLIENT_VERSION}"
export PACKAGE_NAME="${PACKAGE_NAME}"
EOF

echo ${settings} > /tmp/settings

echo 'reading input openapi specs' >& 2
cat swagger.json > ${OUTPUT_DIR}/swagger.json.unprocessed

source "/tmp/settings"

KUBERNETES_CRD_MODE=true \
GENERATE_APIS=${GENERATE_APIS} \
OPENAPI_SKIP_FETCH_SPEC=true \
OPENAPI_MODEL_LENGTH=${OPENAPI_MODEL_LENGTH} \
KUBERNETES_CRD_GROUP_PREFIX=${KUBERNETES_CRD_GROUP_PREFIX} \
HIDE_GENERATION_TIMESTAMP=${HIDE_GENERATION_TIMESTAMP} \
$(pwd)/python.sh ${OUTPUT_DIR} /tmp/settings
