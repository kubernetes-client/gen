#!/usr/bin/env python3
# Copyright 2026 The Kubernetes Authors.
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

import copy
import unittest

from preprocess_spec import process_swagger


class PythonPreprocessingTest(unittest.TestCase):
    def test_preserves_python_client_contracts(self):
        exec_path = '/api/v1/namespaces/{namespace}/pods/{name}/exec'
        portforward_path = (
            '/api/v1/namespaces/{namespace}/pods/{name}/portforward'
        )
        namespace_path = '/api/v1/namespaces/{name}'
        job_path = '/apis/batch/v1/namespaces/{namespace}/jobs/{name}'
        job_collection_path = '/apis/batch/v1/namespaces/{namespace}/jobs'
        pod_path = '/api/v1/namespaces/{namespace}/pods/{name}'
        status_responses = {
            status: {
                'description': 'OK',
                'schema': {
                    '$ref': (
                        '#/definitions/io.k8s.apimachinery.'
                        'pkg.apis.meta.v1.Status'
                    ),
                },
            }
            for status in ('200', '202')
        }
        spec = {
            'swagger': '2.0',
            'info': {'version': 'v1.0.0'},
            'paths': {
                exec_path: {
                    'parameters': [{
                        'description': 'argv array',
                        'in': 'query',
                        'name': 'command',
                        'type': 'string',
                    }],
                    'get': {
                        'operationId': 'connectCoreV1GetNamespacedPodExec',
                        'responses': {'200': {'description': 'OK'}},
                        'tags': ['core_v1'],
                    },
                },
                portforward_path: {
                    'parameters': [{
                        'description': 'comma-separated ports',
                        'format': 'int32',
                        'in': 'query',
                        'name': 'ports',
                        'type': 'integer',
                    }],
                    'get': {
                        'operationId': (
                            'connectCoreV1GetNamespacedPodPortforward'
                        ),
                        'responses': {'200': {'description': 'OK'}},
                        'tags': ['core_v1'],
                    },
                },
                namespace_path: {
                    'delete': {
                        'operationId': 'deleteCoreV1Namespace',
                        'responses': copy.deepcopy(status_responses),
                        'tags': ['core_v1'],
                        'x-kubernetes-action': 'delete',
                    },
                },
                job_path: {
                    'delete': {
                        'operationId': 'deleteBatchV1NamespacedJob',
                        'responses': copy.deepcopy(status_responses),
                        'tags': ['batch_v1'],
                        'x-kubernetes-action': 'delete',
                    },
                },
                job_collection_path: {
                    'delete': {
                        'operationId': (
                            'deleteCollectionBatchV1NamespacedJob'
                        ),
                        'responses': {
                            '200': copy.deepcopy(status_responses['200']),
                        },
                        'tags': ['batch_v1'],
                        'x-kubernetes-action': 'deletecollection',
                    },
                },
                pod_path: {
                    'delete': {
                        'operationId': 'deleteCoreV1NamespacedPod',
                        'responses': {
                            status: {
                                'description': 'OK',
                                'schema': {
                                    '$ref': (
                                        '#/definitions/'
                                        'io.k8s.api.core.v1.Pod'
                                    ),
                                },
                            }
                            for status in ('200', '202')
                        },
                        'tags': ['core_v1'],
                        'x-kubernetes-action': 'delete',
                    },
                },
            },
            'definitions': {
                'io.k8s.apimachinery.pkg.apis.meta.v1.GroupVersionKind': {
                    'type': 'object',
                    'properties': {},
                },
                'io.k8s.apimachinery.pkg.apis.meta.v1.ListMeta': {
                    'type': 'object',
                    'properties': {},
                },
                'io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta': {
                    'type': 'object',
                    'properties': {},
                },
                'io.k8s.apimachinery.pkg.apis.meta.v1.Status': {
                    'type': 'object',
                    'properties': {},
                },
                'io.k8s.api.core.v1.Namespace': {
                    'type': 'object',
                    'properties': {},
                },
                'io.k8s.api.core.v1.Pod': {
                    'type': 'object',
                    'properties': {},
                },
            },
            'securityDefinitions': {
                'BearerToken': {
                    'in': 'header',
                    'name': 'authorization',
                    'type': 'apiKey',
                },
            },
        }

        processed = process_swagger(copy.deepcopy(spec), 'python')
        async_processed = process_swagger(
            copy.deepcopy(spec), 'python-asyncio'
        )
        non_python = process_swagger(copy.deepcopy(spec), 'java')

        self.assertEqual(processed, async_processed)

        command = processed['paths'][exec_path]['parameters'][0]
        self.assertEqual('array', command['type'])
        self.assertEqual({'type': 'string'}, command['items'])
        self.assertEqual('multi', command['collectionFormat'])
        ports = processed['paths'][portforward_path]['parameters'][0]
        self.assertEqual('string', ports['type'])
        self.assertNotIn('format', ports)
        self.assertEqual(
            'authorization',
            processed['securityDefinitions']['BearerToken'][
                'x-auth-id-alias'
            ],
        )
        self.assertEqual(
            ['application/merge-patch+json'],
            processed['paths'][
                '/apis/{group}/{version}/{plural}/{name}'
            ]['patch']['consumes'],
        )
        self.assertNotIn(
            'x-auth-id-alias',
            non_python['securityDefinitions']['BearerToken'],
        )
        self.assertEqual(
            'string',
            non_python['paths'][exec_path]['parameters'][0]['type'],
        )
        self.assertEqual(
            'integer',
            non_python['paths'][portforward_path]['parameters'][0]['type'],
        )
        for path in (namespace_path, job_path):
            for status in ('200', '202'):
                with self.subTest(path=path, status=status):
                    self.assertEqual(
                        {'type': 'object'},
                        processed['paths'][path]['delete'][
                            'responses'
                        ][status]['schema'],
                    )
                    self.assertEqual(
                        {'$ref': '#/definitions/v1.Status'},
                        non_python['paths'][path]['delete'][
                            'responses'
                        ][status]['schema'],
                    )

        self.assertEqual(
            {'$ref': '#/definitions/v1.Status'},
            processed['paths'][job_collection_path]['delete'][
                'responses'
            ]['200']['schema'],
        )
        for status in ('200', '202'):
            with self.subTest(status=status):
                self.assertEqual(
                    {'$ref': '#/definitions/v1.Pod'},
                    processed['paths'][pod_path]['delete'][
                        'responses'
                    ][status]['schema'],
                )


if __name__ == '__main__':
    unittest.main()
