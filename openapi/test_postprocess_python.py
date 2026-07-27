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

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class PythonPostprocessingTest(unittest.TestCase):
    def test_rewrites_generated_package_references(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            docs_directory = output_directory / "docs"
            package_directory = output_directory / "client"
            docs_directory.mkdir()
            package_directory.mkdir()

            readme = output_directory / "README.md"
            model_doc = docs_directory / "V1Pod.md"
            service_doc = docs_directory / "V1ServicePort.md"
            json_schema_doc = docs_directory / "V1JSONSchemaProps.md"
            package_init = package_directory / "__init__.py"
            module = package_directory / "api_client.py"
            service_model = package_directory / "v1_service_port.py"
            tcp_socket_model = package_directory / "v1_tcp_socket_action.py"
            json_schema_model = (
                package_directory / "v1_json_schema_props.py"
            )
            readme.write_text(
                "# client\n\n"
                "Use client.CoreV1Api.  \n"
                "import client\n"
                "from client.api_client import ApiClient\n"
                "The client is configured here.\n"
                "This is a generated client.\n"
                "Install client-python or kubernetes-client.\n"
                "Already qualified: kubernetes.client.CoreV1Api.\n\n"
            )
            model_doc.write_text("See client.V1Pod.\t\n\n")
            service_doc.write_text(
                "**target_port** | **object** | target | [optional]\n"
                "**metadata** | **object** | metadata | [optional]\n"
            )
            json_schema_doc.write_text(
                "**additional_items** | **object** | items | [optional]\n"
                "**additional_properties** | **object** | props | [optional]\n"
                "**default** | **object** | default | [optional]\n"
                "**dependencies** | **Dict[str, object]** | deps | [optional]\n"
                "**enum** | **List[object]** | enum | [optional]\n"
                "**example** | **object** | example | [optional]\n"
                "**items** | **object** | items | [optional]\n"
                "**properties** | **Dict[str, object]** | props | [optional]\n"
            )
            package_init.write_text(
                '__all__ = ["ApiClient"]\n\n'
                "import typing as _typing\n\n"
                "if _typing.TYPE_CHECKING:\n"
                "    from client.api_client import ApiClient\n"
                "else:\n"
                "    from importlib import import_module\n\n"
                '    _exports = {"ApiClient": ".api_client"}\n\n'
                "    def __getattr__(name: str) -> object:\n"
                "        if (module_name := _exports.get(name)) is None:\n"
                '            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")\n'
                "        value = getattr(import_module(module_name, __name__), name)\n"
                "        globals()[name] = value\n"
                "        return value\n\n"
                "    def __dir__() -> list[str]:\n"
                "        return sorted(globals().keys() | _exports.keys())\n"
            )
            module.write_text(
                "from pydantic import validate_call, Field\n"
                "import client.models  \n"
                "from client.api_client import ApiClient\n"
                'MODEL = getattr(client.models, "V1Pod")\n\n'
                "class CoreV1Api:\n"
                "    @validate_call\n"
                "    def patch_namespaced_pod(\n"
                "        self,\n"
                "        body: Dict[str, Any],\n"
                "    ): ...\n\n"
                "    def patch_custom_object(\n"
                "        self,\n"
                '        body: Annotated[Dict[str, Any], Field(description="patch")],\n'
                "    ): ...\n\n"
                "    def create_namespaced_pod(\n"
                "        self,\n"
                "        body: Dict[str, Any],\n"
                "    ): ...\n\n"
            )
            service_model.write_text(
                "from pydantic import Field, StrictInt\n\n"
                "class V1ServicePort:\n"
                "    target_port: Optional[Dict[str, Any]] = None\n"
                "    metadata: Optional[Dict[str, Any]] = None\n"
            )
            tcp_socket_model.write_text(
                "from pydantic import Field, StrictStr\n\n"
                "class V1TCPSocketAction:\n"
                "    port: Dict[str, Any]\n"
            )
            json_schema_model.write_text(
                "class V1JSONSchemaProps:\n"
                "    additional_items: Optional[Dict[str, Any]] = None\n"
                "    additional_properties: Optional[Dict[str, Any]] = None\n"
                "    default: Optional[Dict[str, Any]] = None\n"
                "    dependencies: Optional[Dict[str, Dict[str, Any]]] = None\n"
                "    enum: Optional[List[Dict[str, Any]]] = None\n"
                "    example: Optional[Dict[str, Any]] = None\n"
                "    items: Optional[Dict[str, Any]] = None\n"
                "    properties: Optional[Dict[str, Dict[str, Any]]] = None\n"
            )

            for _ in range(2):
                subprocess.run(
                    [
                        sys.executable,
                        str(Path(__file__).with_name("postprocess_python.py")),
                        str(output_directory),
                        "client",
                        "urllib3",
                        "kubernetes",
                    ],
                    check=True,
                )

            self.assertEqual(
                "# kubernetes.client\n\n"
                "Use kubernetes.client.CoreV1Api.\n"
                "import kubernetes.client\n"
                "from kubernetes.client.api_client import ApiClient\n"
                "The client is configured here.\n"
                "This is a generated client.\n"
                "Install client-python or kubernetes-client.\n"
                "Already qualified: kubernetes.client.CoreV1Api.\n",
                readme.read_text(),
            )
            self.assertEqual(
                "See kubernetes.client.V1Pod.\n",
                model_doc.read_text(),
            )
            self.assertEqual(
                "**target_port** | **Union[int, str]** | target | [optional]\n"
                "**metadata** | **object** | metadata | [optional]\n",
                service_doc.read_text(),
            )
            self.assertEqual(
                "**additional_items** | **Union[Dict[str, Any], bool]** | items | [optional]\n"
                "**additional_properties** | **Union[Dict[str, Any], bool]** | props | [optional]\n"
                "**default** | **Any** | default | [optional]\n"
                "**dependencies** | **Dict[str, Union[Dict[str, Any], List[str]]]** | deps | [optional]\n"
                "**enum** | **List[Any]** | enum | [optional]\n"
                "**example** | **Any** | example | [optional]\n"
                "**items** | **Union[Dict[str, Any], List[Dict[str, Any]]]** | items | [optional]\n"
                "**properties** | **Dict[str, object]** | props | [optional]\n",
                json_schema_doc.read_text(),
            )
            self.assertEqual(
                '__all__ = ["ApiClient"]\n\n'
                "import typing as _typing\n\n"
                "if _typing.TYPE_CHECKING:\n"
                "    from kubernetes.client.api_client import ApiClient\n"
                "else:\n"
                "    from importlib import import_module\n\n"
                '    _exports = {"ApiClient": ".api_client"}\n\n'
                "    def __getattr__(name: str) -> object:\n"
                "        if (module_name := _exports.get(name)) is None:\n"
                '            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")\n'
                "        value = getattr(import_module(module_name, __name__), name)\n"
                "        globals()[name] = value\n"
                "        return value\n\n"
                "    def __dir__() -> list[str]:\n"
                "        return sorted(globals().keys() | _exports.keys())\n",
                package_init.read_text(),
            )
            self.assertEqual(
                "from pydantic import BaseModel, validate_call, Field\n"
                "import kubernetes.client.models\n"
                "from kubernetes.client.api_client import ApiClient\n"
                'MODEL = getattr(kubernetes.client.models, "V1Pod")\n\n'
                "class CoreV1Api:\n"
                "    @validate_call(config={'defer_build': True})\n"
                "    def patch_namespaced_pod(\n"
                "        self,\n"
                "        body: Union[Dict[str, Any], List[Dict[str, Any]], BaseModel],\n"
                "    ): ...\n\n"
                "    def patch_custom_object(\n"
                "        self,\n"
                '        body: Annotated[Union[Dict[str, Any], List[Dict[str, Any]], BaseModel], Field(description="patch")],\n'
                "    ): ...\n\n"
                "    def create_namespaced_pod(\n"
                "        self,\n"
                "        body: Dict[str, Any],\n"
                "    ): ...\n",
                module.read_text(),
            )
            self.assertEqual(
                "from pydantic import Field, StrictInt, StrictStr\n\n"
                "class V1ServicePort:\n"
                "    target_port: Optional[StrictInt | StrictStr] = None\n"
                "    metadata: Optional[Dict[str, Any]] = None\n",
                service_model.read_text(),
            )
            self.assertEqual(
                "from pydantic import Field, StrictInt, StrictStr\n\n"
                "class V1TCPSocketAction:\n"
                "    port: StrictInt | StrictStr\n",
                tcp_socket_model.read_text(),
            )
            self.assertEqual(
                "class V1JSONSchemaProps:\n"
                "    additional_items: Optional[Dict[str, Any] | StrictBool] = None\n"
                "    additional_properties: Optional[Dict[str, Any] | StrictBool] = None\n"
                "    default: Any = None\n"
                "    dependencies: Optional[Dict[str, Dict[str, Any] | List[str]]] = None\n"
                "    enum: Optional[List[Any]] = None\n"
                "    example: Any = None\n"
                "    items: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None\n"
                "    properties: Optional[Dict[str, Dict[str, Any]]] = None\n",
                json_schema_model.read_text(),
            )

    def test_preserves_independent_async_namespace_and_raw_transport(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            docs_directory = output_directory / "docs"
            package_directory = output_directory / "client"
            api_directory = package_directory / "api"
            docs_directory.mkdir()
            api_directory.mkdir(parents=True)

            readme = output_directory / "README.md"
            model_doc = docs_directory / "V1Pod.md"
            api_client = package_directory / "api_client.py"
            module = api_directory / "core_v1_api.py"
            readme.write_text(
                "# client\n\n"
                "Use client.CoreV1Api.\n"
                "from client.api_client import ApiClient\n"
            )
            model_doc.write_text("See client.V1Pod.\n")
            api_client.write_text(
                "class ApiClient:\n"
                "    async def call_api(\n"
                "        self,\n"
                "        _request_timeout=None\n"
                "    ) -> rest.RESTResponse:\n"
                "        return response\n"
            )
            module.write_text(
                "from client.api_client import ApiClient\n\n"
                "class CoreV1Api:\n"
                "    async def read_pod_without_preload_content(\n"
                "        self,\n"
                "    ):\n"
                "        response_data = await self.api_client.call_api(\n"
                "            *_param,\n"
                "            _request_timeout=_request_timeout,\n"
                "        )\n"
                "        return response_data.response\n"
            )

            for _ in range(2):
                subprocess.run(
                    [
                        sys.executable,
                        str(Path(__file__).with_name("postprocess_python.py")),
                        str(output_directory),
                        "client",
                        "asyncio",
                        "kubernetes_asyncio",
                    ],
                    check=True,
                )

            self.assertEqual(
                "# kubernetes_asyncio.client\n\n"
                "Use kubernetes_asyncio.client.CoreV1Api.\n"
                "from kubernetes_asyncio.client.api_client import ApiClient\n",
                readme.read_text(),
            )
            self.assertEqual(
                "See kubernetes_asyncio.client.V1Pod.\n",
                model_doc.read_text(),
            )
            self.assertEqual(
                "class ApiClient:\n"
                "    async def call_api(\n"
                "        self,\n"
                "        _request_timeout=None,\n"
                "        _preload_content=True,\n"
                "    ) -> rest.RESTResponse:\n"
                "        return response\n",
                api_client.read_text(),
            )
            self.assertEqual(
                "from kubernetes_asyncio.client.api_client import ApiClient\n\n"
                "class CoreV1Api:\n"
                "    async def read_pod_without_preload_content(\n"
                "        self,\n"
                "    ):\n"
                "        response_data = await self.api_client.call_api(\n"
                "            *_param,\n"
                "            _preload_content=False,\n"
                "            _request_timeout=_request_timeout,\n"
                "        )\n"
                "        return response_data.response\n",
                module.read_text(),
            )

    def test_rewrites_async_client_without_changing_sync_imports(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory)
            docs_directory = output_directory / "docs"
            package_directory = output_directory / "client"
            api_directory = package_directory / "api"
            docs_directory.mkdir()
            api_directory.mkdir(parents=True)

            readme = output_directory / "README.md"
            model_doc = docs_directory / "V1Pod.md"
            configuration = package_directory / "configuration.py"
            api_client = package_directory / "api_client.py"
            rest = package_directory / "rest.py"
            module = api_directory / "core_v1_api.py"
            readme.write_text(
                "# client\n\n"
                "Use client.CoreV1Api.\n"
                "from client.api_client import ApiClient\n"
            )
            model_doc.write_text("See client.V1Pod.\n")
            configuration.write_text(
                "import aiohttp\n\n"
                "class Configuration:\n"
                "    def get_api_key_with_prefix(self, identifier):\n"
                "        if self.refresh_api_key_hook is not None:\n"
                "            self.refresh_api_key_hook(self)\n"
                "        return self.api_key.get(identifier)\n\n"
                "    def auth_settings(self):\n"
                "        return {\n"
                "            'BearerToken': {\n"
                "                'value': self.get_api_key_with_prefix(\n"
                "                    'BearerToken',\n"
                "                ),\n"
                "            },\n"
                "        }\n"
            )
            api_client.write_text(
                "class ApiClient:\n"
                "    def param_serialize(self, auth_settings):\n"
                "        self.update_params_for_auth(\n"
                "            auth_settings,\n"
                "        )\n\n"
                "    def update_params_for_auth(\n"
                "        self, auth_settings,\n"
                "    ):\n"
                "        for auth in auth_settings:\n"
                "            auth_setting = "
                "self.configuration.auth_settings().get(auth)\n"
            )
            rest.write_text(
                "import re\n"
                "import ssl\n\n"
                "class RESTClientObject:\n"
                "    def __init__(self, configuration):\n"
                "        self.configuration = configuration\n"
                "        self.proxy = configuration.proxy\n\n"
                "    def _create_pool_manager(self):\n"
                "        kwargs = {\n"
                '            "trust_env": True,\n'
                "        }\n"
                "        return kwargs\n\n"
                "    async def request(self, method, headers, body):\n"
                "        args = {}\n"
                "        if self.proxy:\n"
                '            args["proxy"] = self.proxy\n'
                "        # For `POST`, `PUT`, `PATCH`, `OPTIONS`, `DELETE`\n"
                "        if method in ['POST', 'PATCH']:\n"
                "            if re.search('json', headers['Content-Type'], "
                "re.IGNORECASE):\n"
                "                args['data'] = body\n"
            )
            module.write_text(
                "from pydantic import validate_call, Field\n"
                "import client.models\n"
                "from client.api_client import ApiClient\n\n"
                "class CoreV1Api:\n"
                "    @validate_call\n"
                "    async def patch_namespaced_pod(\n"
                "        self,\n"
                "        body: Dict[str, Any],\n"
                "    ):\n"
                "        _param = self._patch_namespaced_pod_serialize(\n"
                "            body=body,\n"
                "        )\n"
                "        return _param\n\n"
                "    @validate_call\n"
                "    async def create_namespaced_pod(\n"
                "        self,\n"
                "        body: Dict[str, Any],\n"
                "    ): ...\n\n"
                "    def _patch_namespaced_pod_serialize(self, body):\n"
                "        return self.api_client.param_serialize(\n"
                "            body,\n"
                "        )\n"
            )

            for _ in range(2):
                subprocess.run(
                    [
                        sys.executable,
                        str(Path(__file__).with_name("postprocess_python.py")),
                        str(output_directory),
                        "client",
                        "asyncio",
                        "kubernetes.aio",
                    ],
                    check=True,
                )

            self.assertEqual(
                "# kubernetes.aio.client\n\n"
                "Use kubernetes.aio.client.CoreV1Api.\n"
                "from kubernetes.aio.client.api_client import ApiClient\n",
                readme.read_text(),
            )
            self.assertEqual(
                "See kubernetes.aio.client.V1Pod.\n", model_doc.read_text()
            )
            self.assertEqual(
                "import asyncio\n"
                "import aiohttp\n\n"
                "class Configuration:\n"
                "    async def get_api_key_with_prefix(self, identifier):\n"
                "        if self.refresh_api_key_hook is not None:\n"
                "            result = self.refresh_api_key_hook(self)\n"
                "            if asyncio.iscoroutine(result):\n"
                "                await result\n"
                "        return self.api_key.get(identifier)\n\n"
                "    async def auth_settings(self):\n"
                "        return {\n"
                "            'BearerToken': {\n"
                "                'value': await self.get_api_key_with_prefix(\n"
                "                    'BearerToken',\n"
                "                ),\n"
                "            },\n"
                "        }\n",
                configuration.read_text(),
            )
            self.assertEqual(
                "class ApiClient:\n"
                "    async def param_serialize(self, auth_settings):\n"
                "        await self.update_params_for_auth(\n"
                "            auth_settings,\n"
                "        )\n\n"
                "    async def update_params_for_auth(\n"
                "        self, auth_settings,\n"
                "    ):\n"
                "        for auth in auth_settings:\n"
                "            auth_setting = "
                "(await self.configuration.auth_settings()).get(auth)\n",
                api_client.read_text(),
            )
            rest_text = rest.read_text()
            self.assertIn('"read_bufsize": 2**21,\n', rest_text)
            self.assertIn(
                "if configuration.disable_strict_ssl_verification:\n",
                rest_text,
            )
            self.assertIn(
                'args["server_hostname"] = '
                "self.configuration.tls_server_name\n",
                rest_text,
            )
            self.assertIn(
                "headers['Content-Type'] = "
                "'application/strategic-merge-patch+json'\n",
                rest_text,
            )
            self.assertIn(
                "or headers['Content-Type'] == "
                "'application/apply-patch+yaml'\n",
                rest_text,
            )
            self.assertEqual(1, rest_text.count('"read_bufsize": 2**21,'))
            self.assertEqual(
                "from pydantic import BaseModel, validate_call, Field\n"
                "import kubernetes.aio.client.models\n"
                "from kubernetes.aio.client.api_client import ApiClient\n\n"
                "class CoreV1Api:\n"
                "    @validate_call(config={'defer_build': True})\n"
                "    async def patch_namespaced_pod(\n"
                "        self,\n"
                "        body: Union[Dict[str, Any], "
                "List[Dict[str, Any]], BaseModel],\n"
                "    ):\n"
                "        _param = "
                "await self._patch_namespaced_pod_serialize(\n"
                "            body=body,\n"
                "        )\n"
                "        return _param\n\n"
                "    @validate_call(config={'defer_build': True})\n"
                "    async def create_namespaced_pod(\n"
                "        self,\n"
                "        body: Dict[str, Any],\n"
                "    ): ...\n\n"
                "    async def _patch_namespaced_pod_serialize(self, body):\n"
                "        return await self.api_client.param_serialize(\n"
                "            body,\n"
                "        )\n",
                module.read_text(),
            )


if __name__ == "__main__":
    unittest.main()
