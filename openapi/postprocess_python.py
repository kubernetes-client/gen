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

import argparse
import re
from pathlib import Path


parser = argparse.ArgumentParser(
    description="Post-process the generated Python client."
)
parser.add_argument("output_directory", type=Path)
parser.add_argument("package_name")
parser.add_argument("library", choices=("urllib3", "asyncio"))
parser.add_argument(
    "namespace",
    choices=("kubernetes", "kubernetes.aio", "kubernetes_asyncio"),
)
args = parser.parse_args()

qualified_package_name = f"{args.namespace}.{args.package_name}"

# Swagger 2 exposes these IntOrString fields as free-form objects, which makes
# the generated Pydantic validators reject valid scalar values. Kubernetes
# serializes them as the contained integer or string:
# https://github.com/kubernetes/kubernetes/blob/8ba6370120c1371ab70428be16341c3cf6ba8584/staging/src/k8s.io/apimachinery/pkg/util/intstr/intstr.go#L32-L45
int_or_string_fields = {
    "v1httpgetaction": ("port",),
    "v1networkpolicyport": ("port",),
    "v1poddisruptionbudgetspec": ("max_unavailable", "min_available"),
    "v1rollingupdatedaemonset": ("max_surge", "max_unavailable"),
    "v1rollingupdatedeployment": ("max_surge", "max_unavailable"),
    "v1rollingupdatestatefulsetstrategy": ("max_unavailable",),
    "v1serviceport": ("target_port",),
    "v1tcpsocketaction": ("port",),
}

# kube-openapi cannot describe these JSONSchemaProps unions until it supports
# anyOf. Preserve the Kubernetes JSON contract in generated validators/docs:
# https://github.com/kubernetes/kubernetes/blob/8ba6370120c1371ab70428be16341c3cf6ba8584/staging/src/k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1/types_jsonschema.go#L75-L112
# https://github.com/kubernetes/kubernetes/blob/8ba6370120c1371ab70428be16341c3cf6ba8584/staging/src/k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1/types_jsonschema.go#L348-L403
json_schema_props_fields = {
    "additional_items": (
        "Optional[Dict[str, Any]]",
        "Optional[Dict[str, Any] | StrictBool]",
        "object",
        "Union[Dict[str, Any], bool]",
    ),
    "additional_properties": (
        "Optional[Dict[str, Any]]",
        "Optional[Dict[str, Any] | StrictBool]",
        "object",
        "Union[Dict[str, Any], bool]",
    ),
    "default": ("Optional[Dict[str, Any]]", "Any", "object", "Any"),
    "dependencies": (
        "Optional[Dict[str, Dict[str, Any]]]",
        "Optional[Dict[str, Dict[str, Any] | List[str]]]",
        "Dict[str, object]",
        "Dict[str, Union[Dict[str, Any], List[str]]]",
    ),
    "enum": (
        "Optional[List[Dict[str, Any]]]",
        "Optional[List[Any]]",
        "List[object]",
        "List[Any]",
    ),
    "example": ("Optional[Dict[str, Any]]", "Any", "object", "Any"),
    "items": (
        "Optional[Dict[str, Any]]",
        "Optional[Dict[str, Any] | List[Dict[str, Any]]]",
        "object",
        "Union[Dict[str, Any], List[Dict[str, Any]]]",
    ),
}

markdown_files = [args.output_directory / "README.md"]
markdown_files.extend((args.output_directory / "docs").rglob("*.md"))
python_files = (args.output_directory / args.package_name).rglob("*.py")

for path, file_type in [
    *((path, "markdown") for path in markdown_files),
    *((path, "python") for path in python_files),
]:
    text = path.read_text()
    if file_type == "markdown":
        if path.name == "README.md":
            text = re.sub(
                r"\A# client(?=\r?\n|\Z)",
                f"# {qualified_package_name}",
                text,
            )
        text = re.sub(
            r"(?<![\w.-])client(?=\.[A-Za-z_])",
            qualified_package_name,
            text,
        )
        text = re.sub(
            r"(?m)^(\s*(?:from|import)\s+)client(?=[.\s]|$)",
            rf"\1{qualified_package_name}",
            text,
        )
        for field in int_or_string_fields.get(path.stem.lower(), ()):
            text = text.replace(
                f"**{field}** | **object** |",
                f"**{field}** | **Union[int, str]** |",
            )
        if path.stem == "V1JSONSchemaProps":
            for field, (_, _, old_type, new_type) in (
                json_schema_props_fields.items()
            ):
                text = text.replace(
                    f"**{field}** | **{old_type}** |",
                    f"**{field}** | **{new_type}** |",
                )
    elif args.package_name == "client":
        text = text.replace(
            "import client.", f"import {qualified_package_name}."
        )
        text = text.replace(
            "from client", f"from {qualified_package_name}"
        )
        text = text.replace(
            "getattr(client.models",
            f"getattr({qualified_package_name}.models",
        )
        # Building every API method's Pydantic schema at import time is
        # expensive. defer_build is supported for validate_call since 2.11:
        # https://github.com/pydantic/pydantic/commit/8e98bc0a66379e693780eb6edd611f4177c60c30
        text = text.replace(
            "@validate_call\n",
            "@validate_call(config={'defer_build': True})\n",
        )
        if args.library == "asyncio":
            if path.name == "configuration.py":
                if "import asyncio\n" not in text:
                    text = text.replace(
                        "import aiohttp\n", "import asyncio\nimport aiohttp\n"
                    )
                text = text.replace(
                    "    def get_api_key_with_prefix(",
                    "    async def get_api_key_with_prefix(",
                )
                # Kubernetes token hooks can perform asynchronous refresh:
                # https://github.com/kubernetes-client/python/blob/ed9ffd4c3c4bee083c1a585a9559257ea02700eb/scripts/asyncio/client_configuration_async_refresh_api_key_hook.diff
                text = text.replace(
                    "        if self.refresh_api_key_hook is not None:\n"
                    "            self.refresh_api_key_hook(self)\n",
                    "        if self.refresh_api_key_hook is not None:\n"
                    "            result = self.refresh_api_key_hook(self)\n"
                    "            if asyncio.iscoroutine(result):\n"
                    "                await result\n",
                )
                text = text.replace(
                    "    def auth_settings(", "    async def auth_settings("
                )
                text = text.replace(
                    "'value': self.get_api_key_with_prefix(\n",
                    "'value': await self.get_api_key_with_prefix(\n",
                )
                if "self.disable_strict_ssl_verification = False\n" not in text:
                    text = text.replace(
                        "        self.verify_ssl = verify_ssl\n",
                        "        self.verify_ssl = verify_ssl\n"
                        "        self.disable_strict_ssl_verification = False\n",
                    )
            elif path.name == "api_client.py":
                text = text.replace(
                    "    def param_serialize(",
                    "    async def param_serialize(",
                )
                text = text.replace(
                    "        self.update_params_for_auth(\n",
                    "        await self.update_params_for_auth(\n",
                )
                text = text.replace(
                    "    def update_params_for_auth(\n",
                    "    async def update_params_for_auth(\n",
                )
                text = text.replace(
                    "self.configuration.auth_settings().get(auth)",
                    "(await self.configuration.auth_settings()).get(auth)",
                )
                text = text.replace(
                    "        _request_timeout=None\n"
                    "    ) -> rest.RESTResponse:\n",
                    "        _request_timeout=None,\n"
                    "        _preload_content=True,\n"
                    "    ) -> rest.RESTResponse:\n",
                )
            elif path.name == "rest.py":
                if '"read_bufsize": 2**21,' not in text:
                    text = text.replace(
                        '            "trust_env": True,\n',
                        '            "trust_env": True,\n'
                        "            # Kubernetes watch events can exceed "
                        "aiohttp's default buffer.\n"
                        '            "read_bufsize": 2**21,\n',
                    )
                if "if configuration.disable_strict_ssl_verification:\n" not in text:
                    text = text.replace(
                        "        self.proxy = configuration.proxy\n",
                        "        if configuration.disable_strict_ssl_verification:\n"
                        "            self.ssl_context.verify_flags "
                        "&= ~ssl.VERIFY_X509_STRICT\n\n"
                        "        self.proxy = configuration.proxy\n",
                    )
                if 'args["server_hostname"]' not in text:
                    text = text.replace(
                        "        if self.proxy:\n",
                        "        if self.configuration.tls_server_name:\n"
                        '            args["server_hostname"] = '
                        "self.configuration.tls_server_name\n\n"
                        "        if self.proxy:\n",
                    )
                if (
                    "# JSON Patch contains operations; "
                    "object patches use strategic merge.\n"
                ) not in text:
                    text = text.replace(
                        "        # For `POST`, `PUT`, `PATCH`, `OPTIONS`, `DELETE`\n",
                        "        # JSON Patch contains operations; "
                        "object patches use strategic merge.\n"
                        "        # https://kubernetes.io/docs/reference/using-api/api-concepts/#updates-to-existing-resources\n"
                        "        if (\n"
                        "            method == 'PATCH'\n"
                        "            and headers['Content-Type'] == "
                        "'application/json-patch+json'\n"
                        "            and not isinstance(body, list)\n"
                        "        ):\n"
                        "            headers['Content-Type'] = "
                        "'application/strategic-merge-patch+json'\n\n"
                        "        # For `POST`, `PUT`, `PATCH`, `OPTIONS`, `DELETE`\n",
                    )
                if (
                    "headers['Content-Type'] == "
                    "'application/apply-patch+yaml'"
                ) not in text:
                    text = text.replace(
                        "            if re.search('json', headers['Content-Type'], "
                        "re.IGNORECASE):\n",
                        "            if (\n"
                        "                re.search('json', headers['Content-Type'], "
                        "re.IGNORECASE)\n"
                        "                or headers['Content-Type'] == "
                        "'application/apply-patch+yaml'\n"
                        "            ):\n",
                    )
            elif path.parent.name == "api":
                text = re.sub(
                    r"(?m)^    def (_[A-Za-z_][A-Za-z0-9_]*_serialize\()",
                    r"    async def \1",
                    text,
                )
                text = text.replace(
                    "        _param = self._",
                    "        _param = await self._",
                )
                text = text.replace(
                    "        return self.api_client.param_serialize(\n",
                    "        return await self.api_client.param_serialize(\n",
                )
                # Websocket exec and attach must distinguish buffered calls
                # from the generated raw-response operations.
                text = re.sub(
                    r"(?ms)(^    async def "
                    r"[A-Za-z_][A-Za-z0-9_]*_without_preload_content\("
                    r".*?^        response_data = "
                    r"await self\.api_client\.call_api\(\n"
                    r"            \*_param,\n)"
                    r"(?!            _preload_content=False,\n)",
                    r"\1            _preload_content=False,\n",
                    text,
                )
    # Generated files otherwise fail git diff --check on trailing whitespace
    # and extra blank lines at EOF.
    lines = text.splitlines()
    if file_type == "python":
        int_or_string = int_or_string_fields.get(
            path.stem.replace("_", "").lower(), ()
        )
        if int_or_string:
            for index, line in enumerate(lines):
                if line.startswith("from pydantic import "):
                    if "StrictInt" not in line:
                        if "StrictStr" in line:
                            line = line.replace(
                                ", StrictStr", ", StrictInt, StrictStr"
                            )
                        else:
                            line += ", StrictInt"
                    if "StrictStr" not in line:
                        line += ", StrictStr"
                    lines[index] = line
                    break
        for field in int_or_string:
            lines = [
                line.replace(
                    f"    {field}: Optional[Dict[str, Any]]",
                    f"    {field}: Optional[StrictInt | StrictStr]",
                ).replace(
                    f"    {field}: Dict[str, Any]",
                    f"    {field}: StrictInt | StrictStr",
                )
                for line in lines
            ]
        if path.stem == "v1_json_schema_props":
            for field, (old_type, new_type, _, _) in (
                json_schema_props_fields.items()
            ):
                lines = [
                    line.replace(
                        f"    {field}: {old_type}",
                        f"    {field}: {new_type}",
                    )
                    for line in lines
                ]
        if any(
            line.startswith(("    def patch_", "    async def patch_"))
            for line in lines
        ):
            lines = [
                line.replace(
                    "from pydantic import validate_call, ",
                    "from pydantic import BaseModel, validate_call, ",
                )
                for line in lines
            ]
        patch_method = False
        for index, line in enumerate(lines):
            if line.startswith(("    def ", "    async def ")):
                patch_method = line.startswith(
                    ("    def patch_", "    async def patch_")
                )
            if patch_method:
                # Swagger 2 describes PATCH bodies as objects, but RFC 6902
                # represents a JSON Patch document as an array of operations:
                # https://www.rfc-editor.org/rfc/rfc6902#section-3
                # Generated request models are also valid object PATCH bodies.
                lines[index] = line.replace(
                    "body: Annotated[Dict[str, Any]",
                    "body: Annotated[Union[Dict[str, Any], List[Dict[str, Any]], BaseModel]",
                ).replace(
                    "body: Dict[str, Any]",
                    "body: Union[Dict[str, Any], List[Dict[str, Any]], BaseModel]",
                )
    while lines and not lines[-1].strip(" \t"):
        lines.pop()
    path.write_text(
        "\n".join(line.rstrip(" \t") for line in lines) + "\n"
    )
