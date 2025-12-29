"""
Quick Controller Sub-Applications Framework

This package provides the core infrastructure for building and managing
sub-applications within Quick Controller. It includes:

- AppContract: Abstract base class for all sub-applications
- AppRegistry: Singleton registry for app registration and lookup
- Permission system: Access control for app-level permissions
"""

from apps.framework.base import AppContract
from apps.framework.permissions import check_app_access, require_app_access
from apps.framework.registry import AppRegistry, get_registry

__all__ = [
    "AppContract",
    "AppRegistry",
    "get_registry",
    "check_app_access",
    "require_app_access",
]
