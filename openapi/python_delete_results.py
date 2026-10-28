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

import re
from collections import defaultdict
from typing import NamedTuple


class DeleteResult(NamedTuple):
    model: str
    api_version: str
    kind: str
    codes: tuple[str, ...]

    @property
    def annotation(self):
        return f"{self.model} | V1Status"


def key(name):
    # Tags and operation IDs retain their spelling but acquire underscores
    # when the Python generator converts them to module and method names.
    return name.replace("_", "").lower()


def wire_type(gvk):
    group, version = gvk["group"], gvk["version"]
    return (f"{group}/{version}" if group else version, gvk["kind"])


def delete_results(spec):
    # Swagger 2 cannot express the two alternatives, but Kubernetes publishes
    # the same group/version/kind on the operation and the resource definition.
    definitions = defaultdict(list)
    for name, schema in spec["definitions"].items():
        for gvk in schema.get("x-kubernetes-group-version-kind", ()):
            definitions[wire_type(gvk)].append(name)

    results = defaultdict(dict)
    for path in spec["paths"].values():
        delete = path.get("delete", {})
        if delete.get("x-kubernetes-action") != "delete":
            continue
        if not (gvk := delete.get("x-kubernetes-group-version-kind")):
            continue
        api_version, kind = wire_type(gvk)
        names = definitions[api_version, kind]
        if len(names) != 1:
            raise ValueError(
                f"{delete['operationId']}: expected one definition for {gvk}, found {names}"
            )
        (name,) = names
        codes = tuple(code for code in delete["responses"] if code.startswith("2"))
        if not codes or any(
            code not in ("200", "202") or delete["responses"][code].get("schema")
            not in ({"type": "object"}, {"$ref": f"#/definitions/{name}"})
            for code in codes
        ):
            continue
        model = "".join(part[:1].upper() + part[1:] for part in name.split("."))
        result = DeleteResult(model, api_version, kind, codes)
        for tag in delete["tags"]:
            results[key(tag + "Api")][key(delete["operationId"])] = result
    return results


def replace_once(text, pattern, replacement, location):
    text, count = re.subn(pattern, replacement, text, flags=re.M)
    if count != 1:
        raise ValueError(f"{location}: expected one match for {pattern!r}, found {count}")
    return text


def update_api(text, results, package):
    blocks = re.split(r"(?=^    (?:async )?def )", text, flags=re.M)
    expected = {name + suffix for name in results for suffix in ("", "withhttpinfo")}
    for i, block in enumerate(blocks):
        if not (match := re.match(r"    (?:async )?def (\w+)\(", block)):
            continue
        method = match[1]
        if not (result := results.get(key(method.removesuffix("_with_http_info")))):
            continue
        expected.remove(key(method))
        if f" import {result.model}\n" not in blocks[0]:
            raise ValueError(f"{method}: generated API did not import {result.model}")
        # Accept already processed input: postprocessing can run more than once.
        old = rf"(?:object|{re.escape(result.annotation)}|{result.model})"
        block = replace_once(
            block, rf"^(    \) -> (?:Tuple\[|ApiResponse\[)?){old}(?=[:,\]])",
            rf"\g<1>{result.annotation}", method,
        )
        for code in result.codes:
            entry = f"            '{code}': "
            block = replace_once(block, f'^{entry}"{old}",', f'{entry}"{result.annotation}",', method)
        blocks[i] = block
    if expected:
        raise ValueError(f"Missing generated DELETE methods: {sorted(expected)}")
    if " import V1Status\n" not in blocks[0]:
        blocks[0] = replace_once(
            blocks[0], rf"^from {re.escape(package)}\.api_client import ",
            f"from {package}.models.v1_status import V1Status\nfrom {package}.api_client import ",
            "V1Status import",
        )
    return "".join(blocks)


def update_docs(text, results):
    sections = text.split("\n# **")
    expected = set(results)
    for i, section in enumerate(sections[1:], 1):
        method = section.partition("**")[0]
        if result := results.get(key(method)):
            expected.remove(key(method))
            section = replace_once(
                section, rf"^> .+? {method}\(", f"> {result.annotation} {method}(", method,
            )
            sections[i] = replace_once(
                section, r"(### Return type\n\n)[^\n]+",
                rf"\1[**{result.model}**]({result.model}.md) or [**V1Status**](V1Status.md)",
                method,
            )
    if expected:
        raise ValueError(f"Missing DELETE documentation: {sorted(expected)}")
    return "\n# **".join(sections)


def update_decoder(text, results):
    models = {("v1", "Status"): "V1Status"}
    for operations in results.values():
        for result in operations.values():
            models[result.api_version, result.kind] = result.model
    table = "_DELETE_MODELS = {\n" + "".join(
        f"    {gvk!r}: {model!r},\n" for gvk, model in sorted(models.items())
    ) + "}\n\n\n"
    text = replace_once(
        text, r"^(?:_DELETE_MODELS = \{\n(?:    [^\n]+\n)*\}\n\n\n)?class ApiClient:",
        table + "class ApiClient:", "_DELETE_MODELS",
    )
    original = "        return self.__deserialize(data, response_type)\n"
    dispatch = """        if isinstance(response_type, str) and response_type.endswith(" | V1Status"):
            match data:
                case {"apiVersion": str(version), "kind": str(kind)}:
                    model = _DELETE_MODELS.get((version, kind))
                    if model not in response_type.split(" | "):
                        raise ValueError(f"Expected {response_type}, got {version}/{kind}")
                    response_type = model
                case _:
                    raise ValueError(f"Expected apiVersion and kind for {response_type}")
"""
    if dispatch not in text:
        text = replace_once(text, re.escape(original), dispatch + original, "DELETE decoder")
    return text
