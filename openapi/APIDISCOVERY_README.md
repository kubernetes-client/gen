# APIDiscovery Definitions

## Overview
This directory contains manually-added OpenAPI v2 definitions for the `apidiscovery.k8s.io/v2beta1` and `apidiscovery.k8s.io/v2` API groups.

## Why is this needed?
The `apidiscovery.k8s.io` API groups (both v2beta1 and v2) exist in Kubernetes and are used for API discovery responses (returned from `/api` and `/apis` endpoints with appropriate accept headers). However, these types are not included in the upstream Kubernetes `swagger.json` file that is downloaded from the repository.

The types exist in the Kubernetes codebase at `k8s.io/api/apidiscovery/v2beta1` and `k8s.io/api/apidiscovery/v2` and have the `+k8s:openapi-gen=true` tag, but they are not exported to the `/openapi/v2` endpoint. This is likely because they are internal system types used for discovery itself rather than resources that can be directly manipulated via typical CRUD operations.

## Types included
The following types are defined in `apidiscovery_definitions.json` for both v2beta1 and v2 API versions:

1. **APIGroupDiscoveryList** - A list of APIGroupDiscovery objects returned from /api and /apis endpoints
2. **APIGroupDiscovery** - Information about which resources are served for an API group
3. **APIVersionDiscovery** - List of resources served for a particular version within an API group
4. **APIResourceDiscovery** - Information about a specific API resource
5. **APISubresourceDiscovery** - Information about an API subresource

## How it works
The definitions are loaded by `preprocess_spec.py` in the `add_apidiscovery_definitions()` function and merged into the swagger spec during preprocessing. The definitions then go through the standard preprocessing pipeline, including:
- Prefix removal (renamed from `io.k8s.api.apidiscovery.v2beta1.*` to `v2beta1.*` and `io.k8s.api.apidiscovery.v2.*` to `v2.*`)
- Reference resolution
- Other standard transformations

## Maintenance
If the apidiscovery types change in future Kubernetes versions, this file may need to be updated. The authoritative source is the upstream Kubernetes repository at:
- Go types: `k8s.io/api/apidiscovery/v2beta1/types.go` and `k8s.io/api/apidiscovery/v2/types.go`
- OpenAPI definitions: `pkg/generated/openapi/zz_generated.openapi.go` (search for `schema_k8sio_api_apidiscovery_v2beta1_` and `schema_k8sio_api_apidiscovery_v2_`)

## Testing
Run `python3 test_apidiscovery.py` to verify that the definitions are properly loaded and integrated into the spec.
Run `./test_integration.sh` for end-to-end testing with a real swagger.json file from kubernetes/kubernetes.
