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
args = parser.parse_args()

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
                r"\A# client(?=\r?\n|\Z)", "# kubernetes.client", text
            )
        text = re.sub(
            r"(?<![\w.-])client(?=\.[A-Za-z_])",
            "kubernetes.client",
            text,
        )
        text = re.sub(
            r"(?m)^(\s*(?:from|import)\s+)client(?=[.\s]|$)",
            r"\1kubernetes.client",
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
        text = text.replace("import client.", "import kubernetes.client.")
        text = text.replace("from client", "from kubernetes.client")
        text = text.replace(
            "getattr(client.models", "getattr(kubernetes.client.models"
        )
        # Building every API method's Pydantic schema at import time is
        # expensive. defer_build is supported for validate_call since 2.11:
        # https://github.com/pydantic/pydantic/commit/8e98bc0a66379e693780eb6edd611f4177c60c30
        text = text.replace(
            "@validate_call\n",
            "@validate_call(config={'defer_build': True})\n",
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
        if any(line.startswith("    def patch_") for line in lines):
            lines = [
                line.replace(
                    "from pydantic import validate_call, ",
                    "from pydantic import BaseModel, validate_call, ",
                )
                for line in lines
            ]
        patch_method = False
        for index, line in enumerate(lines):
            if line.startswith("    def "):
                patch_method = line.startswith("    def patch_")
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
