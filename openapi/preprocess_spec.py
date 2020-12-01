# Copyright 2016 The Kubernetes Authors.
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

from __future__ import print_function

import json
import operator
import os.path
import sys
import argparse
from collections import OrderedDict

import urllib3

# these four constants are shown as part of this example in []:
# "[watch]Pod[List]" is the deprecated version of "[list]Pod?[watch]=True"
WATCH_OP_PREFIX = "watch"
WATCH_OP_SUFFIX = "List"
LIST_OP_PREFIX = "list"
DELETECOLLECTION_OP_PREFIX = "deleteCollection"
WATCH_QUERY_PARAM_NAME = "watch"
ALLOW_WATCH_BOOKMARKS_QUERY_PARAM_NAME = "allowWatchBookmarks"

CUSTOM_OBJECTS_SPEC_PATH = os.path.join(
    os.path.dirname(__file__),
    'custom_objects_spec.json')

_ops = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch']


class PreprocessingException(Exception):
    pass


def _title(s):
    if len(s) == 0:
        return s
    return s[0].upper() + s[1:]


def _to_camel_case(s):
    return ''.join(_title(y) for y in s.split("_"))


def apply_func_to_spec_operations(spec, func, *params):
    """Apply func to each operation in the spec.

    :param spec: The OpenAPI spec to apply func to.
    :param func: the function to apply to the spec's operations. It should be
                 a func(operation, parent) where operation will be each
                 operation of the spec and parent would be the parent object of
                 the given operation.
                 If the return value of the func is True, then the operation
                 will be deleted from the spec.
    """
    for k, v in spec['paths'].items():
        for op in _ops:
            if op not in v:
                continue
            if func(v[op], v, *params):
                del v[op]


def _has_property(prop_list, property_name):
    for prop in prop_list:
        if prop["name"] == property_name:
            return True


def remove_watch_operations(op, parent, operation_ids):
    op_id = op['operationId']
    if not op_id.startswith(WATCH_OP_PREFIX):
        return
    list_id = (LIST_OP_PREFIX +
               op_id.replace(WATCH_OP_SUFFIX, "")[len(WATCH_OP_PREFIX):])
    if list_id not in operation_ids:
        raise PreprocessingException("Cannot find %s" % list_id)
    list_op = operation_ids[list_id]
    params = []
    if 'parameters' in list_op:
        params += list_op['parameters']
    if 'parameters' in parent:
        params += parent['parameters']
    if not _has_property(params, WATCH_QUERY_PARAM_NAME):
        raise PreprocessingException("%s has no watch query param" % list_id)
    return True


def strip_delete_collection_operation_watch_params(op, parent):
    op_id = op['operationId']
    if not op_id.startswith(DELETECOLLECTION_OP_PREFIX):
        return
    params = []
    if 'parameters' in op:
        for i in range(len(op['parameters'])):
            paramName = op['parameters'][i]['name']
            if paramName != WATCH_QUERY_PARAM_NAME and paramName != ALLOW_WATCH_BOOKMARKS_QUERY_PARAM_NAME:
                params.append(op['parameters'][i])
    op['parameters'] = params
    return False


def strip_401_response(operation, _):
    if operation.has_key('responses'):
        operation['responses'].pop('401', None)
        if len(operation['responses']) == 0:
            operation['responses']['200'] = { 'description': 'OK' }


def transform_to_csharp_stream_response(operation, _):
    if operation.get('operationId', None) == 'readNamespacedPodLog' or operation.get('x-kubernetes-action', None) == 'connect':
        operation['responses']['200']["schema"] = {
            "type": "object", 
            "format": "file" ,
        }

def transform_to_csharp_consume_json(operation, _):
    if operation.get('consumes', None) == ["*/*",] or operation.get('consumes', None) == "*/*":
        operation['consumes'] = ["application/json"]

def strip_tags_from_operation_id(operation, _):
    operation_id = operation['operationId']
    if 'tags' in operation:
        for t in operation['tags']:
            operation_id = operation_id.replace(_to_camel_case(t), '')
        operation['operationId'] = operation_id

def clean_crd_meta(spec):
    for k, v in spec['definitions'].items():
        if k.endswith('List'):
            print("Using built-in v1.ListMeta")
            v['properties']['metadata']['$ref'] = '#/definitions/io.k8s.apimachinery.pkg.apis.meta.v1.ListMeta'
            v['properties']['metadata'].pop('properties', None)
        find_rename_ref_recursive(spec, '#/definitions/io.k8s.apimachinery.pkg.apis.meta.v1.ListMeta', '#/definitions/v1.ListMeta')
        find_rename_ref_recursive(spec, '#/definitions/io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta', '#/definitions/v1.ObjectMeta')
        find_rename_ref_recursive(spec, '#/definitions/io.k8s.apimachinery.pkg.apis.meta.v1.Status', '#/definitions/v1.Status')
        find_rename_ref_recursive(spec, '#/definitions/io.k8s.apimachinery.pkg.apis.meta.v1.Patch', '#/definitions/v1.Patch')
        find_rename_ref_recursive(spec, '#/definitions/io.k8s.apimachinery.pkg.apis.meta.v1.DeleteOptions', '#/definitions/v1.DeleteOptions')


def add_custom_objects_spec(spec):
    with open(CUSTOM_OBJECTS_SPEC_PATH, 'r') as custom_objects_spec_file:
        custom_objects_spec = json.loads(custom_objects_spec_file.read())
    for path in custom_objects_spec.keys():
        if path not in spec['paths'].keys():
            spec['paths'][path] = custom_objects_spec[path]
    return spec

def add_codegen_request_body(operation, _):
    if 'parameters' in operation and len(operation['parameters']) > 0:
        if operation['parameters'][0].get('in') == 'body':
            operation['x-codegen-request-body-name'] = 'body'

def drop_paths(spec):
    paths = {}
    if (os.environ.get('GENERATE_APIS') or False):
        group_prefix = os.environ.get('KUBERNETES_CRD_GROUP_PREFIX')
        group_prefix_reversed = '.'.join(group_prefix.split('.')[::-1])
        for k, v in spec['paths'].items():
            if k.startswith('/apis/' + group_prefix_reversed):
                paths[k] = v
            else:
                print("Ignoring non Custom Resource api path %s" %k)
    spec['paths'] = paths


def process_swagger(spec, client_language, crd_mode=False):
    spec = add_custom_objects_spec(spec)

    if crd_mode:
        drop_paths(spec)

    apply_func_to_spec_operations(spec, strip_tags_from_operation_id)

    if client_language == "csharp":
        # 401s in the spec block the csharp code generator from throwing on 401
        apply_func_to_spec_operations(spec, strip_401_response)

        # force to autorest to generate stream
        apply_func_to_spec_operations(spec, transform_to_csharp_stream_response)
        # force to consume json if */* 
        apply_func_to_spec_operations(spec, transform_to_csharp_consume_json)

    apply_func_to_spec_operations(spec, strip_delete_collection_operation_watch_params)

    apply_func_to_spec_operations(spec, add_codegen_request_body)

    operation_ids = {}
    apply_func_to_spec_operations(spec, lambda op, _: operator.setitem(
        operation_ids, op['operationId'], op))

    try:
        apply_func_to_spec_operations(
            spec, remove_watch_operations, operation_ids)
    except PreprocessingException as e:
        print(e)


    if crd_mode:
        filter_api_group(spec)
    remove_model_prefixes(spec, crd_mode)

    inline_primitive_models(spec, preserved_primitives_for_language(client_language))

    if crd_mode:
        clean_crd_meta(spec)

    add_custom_formatting(spec, format_for_language(client_language))
    add_custom_typing(spec, type_for_language(client_language))

    remove_models(spec, removed_models_for_language(client_language))

    add_openapi_codegen_x_implement_extension(spec, client_language)

    return spec

def preserved_primitives_for_language(client_language):
    if client_language == "java":
        return ["intstr.IntOrString", "resource.Quantity", "v1.Patch"]
    elif client_language == "csharp":
        return ["intstr.IntOrString", "resource.Quantity", "v1.Patch"]
    elif client_language == "haskell-http-client":
        return ["intstr.IntOrString", "resource.Quantity"]
    else:
        return []

def format_for_language(client_language):
    if client_language == "java":
        return {"resource.Quantity": "quantity", "v1.Patch": "patch"}
    else:
        return {}

def type_for_language(client_language):
    if client_language == "java":
        return {"v1.Patch": { "type": "string"}}
    elif client_language == "csharp":
        return {
                "v1.Patch": { "type": "object", "properties": {"content": { "type": "object"}} }, 
                "resource.Quantity": { "type": "object", "properties": {"value": { "type": "string"}} }, 
                "intstr.IntOrString" : { "type": "object", "properties": {"value": { "type": "string"}} },
               }
    else:
        return {}

def removed_models_for_language(client_language):
    if client_language == "haskell-http-client":
        return ["intstr.IntOrString", "resource.Quantity"]
    else:
        return []

def rename_model(spec, old_name, new_name):
    if new_name in spec['definitions']:
        raise PreprocessingException(
            "Cannot rename model %s. new name %s exists." %
            (old_name, new_name))
    find_rename_ref_recursive(spec,
                              "#/definitions/" + old_name,
                              "#/definitions/" + new_name)
    spec['definitions'][new_name] = spec['definitions'][old_name]
    del spec['definitions'][old_name]


def find_rename_ref_recursive(root, old, new):
    if isinstance(root, list):
        for r in root:
            find_rename_ref_recursive(r, old, new)
    if isinstance(root, dict):
        if "$ref" in root:
            if root["$ref"] == old:
                root["$ref"] = new
        for k, v in root.items():
            find_rename_ref_recursive(v, old, new)


def is_model_deprecated(m):
    """
    Check if a mode is deprecated model redirection.

    A deprecated mode redirecation has only two members with a
    description starts with "Deprecated." string.
    """
    if len(m) != 2:
        return False
    if "$ref" not in m or "description" not in m:
        return False
    return m["description"].startswith("Deprecated.")

def filter_api_group(spec):
    models = {}
    for k, v in spec['definitions'].items():
        if k.startswith("io.k8s"):
            print("Removing builtin Kubernetes Resource %s" %k)
        elif not k.startswith(os.environ.get('KUBERNETES_CRD_GROUP_PREFIX')):
            print("Ignoring Custom Resource %s" %k)
        else:
            models[k] = v
    spec['definitions'] = models

def remove_deprecated_models(spec):
    """
    In kubernetes 1.8 some of the models are renamed. Our remove_model_prefixes
    still creates the same model names but there are some models added to
    reference old model names to new names. These models broke remove_model_prefixes
    and need to be removed.
    """
    models = {}
    for k, v in spec['definitions'].items():
        if is_model_deprecated(v):
            print("Removing deprecated model %s" % k)
        else:
            models[k] = v
    spec['definitions'] = models


def remove_model_prefixes(spec, crd_mode=False):
    """Remove full package name from OpenAPI model names.

    Starting kubernetes 1.6, all models has full package name. This is
    verbose and inconvenient in python client. This function tries to remove
    parts of the package name but will make sure there is no conflicting model
    names. This will keep most of the model names generated by previous client
    but will change some of them.
    """

    remove_deprecated_models(spec)

    models = {}
    for k, v in spec['definitions'].items():
        if k.startswith("io.k8s"):
            models[k] = {"split_n": 2}
        elif crd_mode and k.startswith(os.environ.get('KUBERNETES_CRD_GROUP_PREFIX')):
            if os.environ.get('OPENAPI_MODEL_LENGTH') or False:
                models[k] = {"split_n": int(os.environ.get('OPENAPI_MODEL_LENGTH'))}

    conflict = True
    while conflict:
        for k, v in models.items():
            splits = k.rsplit(".", v["split_n"])
            v["removed_prefix"] = splits.pop(0)
            v["new_name"] = ".".join(splits)

        conflict = False
        for k, v in models.items():
            for k2, v2 in models.items():
                if k != k2 and v["new_name"] == v2["new_name"]:
                    v["conflict"] = True
                    v2["conflict"] = True
                    conflict = True

        if conflict:
            for k, v in models.items():
                if "conflict" in v:
                    print("Resolving conflict for %s" % k)
                    v["split_n"] += 1
                    del v["conflict"]

    for k, v in models.items():
        if "new_name" not in v:
            raise PreprocessingException("Cannot rename model %s" % k)
        print("Removing prefix %s from %s...\n" % (v["removed_prefix"], k))
        rename_model(spec, k, v["new_name"])


def find_replace_ref_recursive(root, ref_name, replace_map):
    if isinstance(root, list):
        for r in root:
            find_replace_ref_recursive(r, ref_name, replace_map)
    if isinstance(root, dict):
        if "$ref" in root:
            if root["$ref"] == ref_name:
                del root["$ref"]
                for k, v in replace_map.items():
                    if k in root:
                        if k != "description":
                            raise PreprocessingException(
                                "Cannot inline model %s because of "
                                "conflicting key %s." % (ref_name, k))
                        continue
                    root[k] = v
        for k, v in root.items():
            find_replace_ref_recursive(v, ref_name, replace_map)


def remove_models(spec, to_remove_models):
    for k in to_remove_models:
        print("Removing model `%s " % k)
        del spec['definitions'][k]

def inline_primitive_models(spec, excluded_primitives):
    to_remove_models = []
    for k, v in spec['definitions'].items():
        if k in excluded_primitives:
            continue
        if "properties" not in v:
            if k == "intstr.IntOrString":
                v["type"] = "object"
            if "type" not in v:
                v["type"] = "object"
            print("Making model `%s` inline as %s..." % (k, v["type"]))
            find_replace_ref_recursive(spec, "#/definitions/" + k, v)
            to_remove_models.append(k)

    for k in to_remove_models:
        del spec['definitions'][k]

def add_custom_formatting(spec, custom_formats):
    for k, v in spec['definitions'].items():
        if k not in custom_formats:
            continue
        v["format"] = custom_formats[k]

def add_custom_typing(spec, custom_types):
    for k, v in spec['definitions'].items():
        if k not in custom_types:
            continue
        v.update(custom_types[k])

def add_openapi_codegen_x_implement_extension(spec, client_language):
    if client_language != "java":
        return
    if os.environ.get('OPENAPI_SKIP_BASE_INTERFACE') or False:
        return
    for k, v in spec['definitions'].items():
        if "x-kubernetes-group-version-kind" not in v:
            continue
        if k == "v1.Status":
            # Status is explicitly exlucded because it's obviously not a list object
            # but it has ListMeta.
            continue
        if "metadata" not in v['properties']:
            continue # not a legitimate kubernetes api object
        if v["properties"]["metadata"]["$ref"] == "#/definitions/v1.ListMeta":
            v["x-implements"] = ["io.kubernetes.client.common.KubernetesListObject"]
        elif v["properties"]["metadata"]["$ref"] == "#/definitions/v1.ObjectMeta":
            v["x-implements"] = ["io.kubernetes.client.common.KubernetesObject"]



def write_json(filename, object):
    with open(filename, 'w') as out:
        json.dump(object, out, sort_keys=False, indent=2, separators=(',', ': '), ensure_ascii=True)



def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'client_language',
        help='Client language to setup spec for'
    )
    argparser.add_argument(
        'kubernetes_branch',
        help='Branch/tag of github.com/kubernetes/kubernetes to get spec from'
    )
    argparser.add_argument(
        'output_spec_path',
        help='Path to output spec file to'
    )
    argparser.add_argument(
        'username',
        help='Optional username if working on forks',
        default='kubernetes'
    )
    argparser.add_argument(
        'repository',
        help='Optional repository name if working with kubernetes ecosystem projects',
        default='kubernetes'
    )
    args = argparser.parse_args()


    unprocessed_spec = args.output_spec_path + ".unprocessed"
    in_spec = ""
    if os.environ.get("OPENAPI_SKIP_FETCH_SPEC") or False:
        with open(unprocessed_spec, 'r') as content:
            in_spec = json.load(content, object_pairs_hook=OrderedDict)
    else:
        pool = urllib3.PoolManager()
        spec_url = 'https://raw.githubusercontent.com/%s/%s/' \
               '%s/api/openapi-spec/swagger.json' % (args.username,
                                                     args.repository,
                                                     args.kubernetes_branch)
        with pool.request('GET', spec_url, preload_content=False) as response:
            if response.status != 200:
                print("Error downloading spec file %s. Reason: %s" % (spec_url, response.reason))
                return 1
            in_spec = json.load(response, object_pairs_hook=OrderedDict)
    write_json(unprocessed_spec, in_spec)
    # use version from branch/tag name if spec doesn't provide it
    if in_spec['info']['version'] == 'unversioned':
        in_spec['info']['version'] = args.kubernetes_branch
    crd_mode = os.environ.get('KUBERNETES_CRD_MODE') or False
    out_spec = process_swagger(in_spec, args.client_language, crd_mode)
    write_json(args.output_spec_path, out_spec)
    return 0


if __name__ == '__main__':
    sys.exit(main())
