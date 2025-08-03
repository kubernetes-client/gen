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

FROM maven:3.9.11-eclipse-temurin-11

# Install preprocessing script requirements
RUN apt update && \
    apt -y upgrade && \
    apt -y install git python3-pip && \
    apt -y install git python3-urllib3 && \
    pip cache purge && \
    apt autoremove && \
    apt clean

ARG OPENAPI_GENERATOR_COMMIT
ARG GENERATION_XML_FILE
ARG OPENAPI_GENERATOR_USER_ORG=OpenAPITools
ARG OPENAPI_GENERATOR_SOURCE_DIR='/source/openapi-generator'

# Check out specific commit of openapi-generator
RUN mkdir -p ${OPENAPI_GENERATOR_SOURCE_DIR} &&  \
    cd ${OPENAPI_GENERATOR_SOURCE_DIR} && \
    git init --initial-branch=master && \
    git remote add origin https://github.com/${OPENAPI_GENERATOR_USER_ORG}/openapi-generator.git && \
    git fetch --progress --depth=1 origin ${OPENAPI_GENERATOR_COMMIT} && \
    git checkout -b gen FETCH_HEAD && \
    git config --system --add safe.directory ${OPENAPI_GENERATOR_SOURCE_DIR}

# Build it and persist local repository
RUN chmod -R go+rwx /root && \
    umask 0 && \
    cd ${OPENAPI_GENERATOR_SOURCE_DIR} && \
    mvn install -DskipTests -Dmaven.test.skip=true -pl modules/openapi-generator-maven-plugin -am && \
    cp -r /root/.m2/* /usr/share/maven/ref

# Copy required files
COPY openapi-generator/generate_client_in_container.sh /generate_client.sh
COPY preprocess_spec.py /
COPY custom_objects_spec.json /
COPY ${GENERATION_XML_FILE} /generation_params.xml

ENTRYPOINT ["/usr/local/bin/mvn-entrypoint.sh", "/generate_client.sh"]
