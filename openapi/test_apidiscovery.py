#!/usr/bin/env python3
# Copyright 2025 The Kubernetes Authors.
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

"""
Test script to verify that apidiscovery.k8s.io/v2beta1 API definitions
are properly included in the processed OpenAPI spec.
"""

import json
import sys
import os

# Import the preprocessing module
from preprocess_spec import process_swagger, add_apidiscovery_definitions


def test_apidiscovery_definitions_loaded():
    """Test that apidiscovery definitions can be loaded from JSON file."""
    print("Test 1: Loading apidiscovery definitions from JSON file...")
    
    spec = {'definitions': {}}
    spec = add_apidiscovery_definitions(spec)
    
    expected_defs = [
        'io.k8s.api.apidiscovery.v2beta1.APIGroupDiscoveryList',
        'io.k8s.api.apidiscovery.v2beta1.APIGroupDiscovery',
        'io.k8s.api.apidiscovery.v2beta1.APIVersionDiscovery',
        'io.k8s.api.apidiscovery.v2beta1.APIResourceDiscovery',
        'io.k8s.api.apidiscovery.v2beta1.APISubresourceDiscovery'
    ]
    
    for def_name in expected_defs:
        if def_name not in spec['definitions']:
            print(f"  ✗ FAILED: {def_name} not found")
            return False
        print(f"  ✓ {def_name}")
    
    print("  ✓ Test 1 PASSED\n")
    return True


def test_apidiscovery_in_processed_spec():
    """Test that apidiscovery definitions are present in processed spec."""
    print("Test 2: Processing spec with apidiscovery definitions...")
    
    # Create a minimal spec
    minimal_spec = {
        'swagger': '2.0',
        'info': {'version': 'v1.0.0'},
        'paths': {},
        'definitions': {
            'io.k8s.apimachinery.pkg.apis.meta.v1.ListMeta': {
                'type': 'object',
                'properties': {}
            },
            'io.k8s.apimachinery.pkg.apis.meta.v1.ObjectMeta': {
                'type': 'object',
                'properties': {}
            },
            'io.k8s.apimachinery.pkg.apis.meta.v1.GroupVersionKind': {
                'type': 'object',
                'properties': {}
            }
        }
    }
    
    # Process the spec
    processed_spec = process_swagger(minimal_spec, 'python', crd_mode=False)
    
    # After processing, the names should be shortened (remove prefix)
    # Check for v2beta1.* definitions
    apidiscovery_defs = [
        k for k in processed_spec['definitions'].keys() 
        if k.startswith('v2beta1.') and 'API' in k and 'Discovery' in k
    ]
    
    if len(apidiscovery_defs) < 5:
        print(f"  ✗ FAILED: Expected at least 5 apidiscovery definitions, found {len(apidiscovery_defs)}")
        print(f"  Found: {apidiscovery_defs}")
        return False
    
    for def_name in apidiscovery_defs:
        print(f"  ✓ {def_name}")
    
    print("  ✓ Test 2 PASSED\n")
    return True


def test_apidiscovery_structure():
    """Test that apidiscovery definitions have proper structure."""
    print("Test 3: Validating apidiscovery definition structure...")
    
    spec = {'definitions': {}}
    spec = add_apidiscovery_definitions(spec)
    
    # Check APIGroupDiscoveryList structure
    list_def = spec['definitions']['io.k8s.api.apidiscovery.v2beta1.APIGroupDiscoveryList']
    
    required_checks = [
        ('type' in list_def and list_def['type'] == 'object', "type is object"),
        ('properties' in list_def, "has properties"),
        ('items' in list_def['properties'], "has items property"),
        ('x-kubernetes-group-version-kind' in list_def, "has group-version-kind"),
    ]
    
    for check, description in required_checks:
        if not check:
            print(f"  ✗ FAILED: {description}")
            return False
        print(f"  ✓ {description}")
    
    print("  ✓ Test 3 PASSED\n")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing apidiscovery.k8s.io/v2beta1 API definitions")
    print("=" * 70 + "\n")
    
    tests = [
        test_apidiscovery_definitions_loaded,
        test_apidiscovery_in_processed_spec,
        test_apidiscovery_structure,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test raised exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
