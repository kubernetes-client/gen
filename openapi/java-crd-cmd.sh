#!/usr/bin/env bash

PACKAGE_NAME=${PACKAGE_NAME:-io.kubernetes.client}
CLIENT_VERSION=${CLIENT_VERSION:-5.0-SNAPSHOT}
GENERATE_APIS=${GENERATE_APIS:false}
OUTPUT_DIR=${OUTPUT_DIR:-java}
OPENAPI_MODEL_LENGTH=${OPENAPI_MODEL_LENGTH:-}
OPENAPI_SKIP_BASE_INTERFACE=
KUBERNETES_CRD_GROUP_PREFIX=

print_usage() {
  echo "Usage: generate a java project using input openapi spec from stdin" >& 2
  echo " -c: project version of the generated java project." >& 2
  echo " -x: skips implementing kubernetes common interface (this is for backward compatibility w/ client-java lower than 9.0.0)" >& 2
  echo " -n: the prefix of the target CRD's api group to generate." >& 2
  echo " -g: generate crd apis." >& 2
  echo " -p: the base package name of the generated java project. " >& 2
  echo " -o: output directory of the generated java project. " >& 2
  echo " -l: keep the n last segments for the generated class name. " >& 2
}

while getopts 'c:g:n:l:p:o:x' flag; do
  case "${flag}" in
    c) CLIENT_VERSION="${CLIENT_VERSION}" ;;
    g) GENERATE_APIS="${OPTARG}" ;;
    n) KUBERNETES_CRD_GROUP_PREFIX="${OPTARG}" ;;
    l) OPENAPI_MODEL_LENGTH="${OPTARG}" ;;
    p) PACKAGE_NAME="${OPTARG}" ;;
    o) OUTPUT_DIR="${OPTARG}" ;;
    x) OPENAPI_SKIP_BASE_INTERFACE=1 ;;
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
cat > ${OUTPUT_DIR}/swagger.json.unprocessed


source "/tmp/settings"

KUBERNETES_CRD_MODE=true \
GENERATE_APIS=${GENERATE_APIS} \
OPENAPI_SKIP_FETCH_SPEC=true \
OPENAPI_MODEL_LENGTH=${OPENAPI_MODEL_LENGTH} \
KUBERNETES_CRD_GROUP_PREFIX=${KUBERNETES_CRD_GROUP_PREFIX} \
OPENAPI_SKIP_BASE_INTERFACE=${OPENAPI_SKIP_BASE_INTERFACE} \
$(pwd)/java.sh ${OUTPUT_DIR} /tmp/settings
