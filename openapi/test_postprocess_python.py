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


if __name__ == "__main__":
    unittest.main()
