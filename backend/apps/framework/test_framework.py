"""
Test script for the Sub-Applications Framework.

This script demonstrates and validates the core functionality of the framework.
Run with: python -m apps.framework.test_framework
"""

from fastapi import APIRouter

from apps.framework import AppContract, get_registry


class TestApp(AppContract):
    """Example test app implementation."""

    @property
    def app_id(self) -> str:
        return "test_app"

    @property
    def display_name(self) -> str:
        return "Test Application"

    @property
    def icon(self) -> str:
        return "science"

    @property
    def routes(self) -> APIRouter:
        router = APIRouter()

        @router.get("/test")
        async def test_endpoint():
            return {"message": "Test app endpoint"}

        return router

    @property
    def default_access(self) -> bool:
        return True


class SecureApp(AppContract):
    """Example secure app with no default access."""

    @property
    def app_id(self) -> str:
        return "secure_app"

    @property
    def display_name(self) -> str:
        return "Secure Application"

    @property
    def icon(self) -> str:
        return "lock"

    @property
    def routes(self) -> APIRouter:
        router = APIRouter()

        @router.get("/secure")
        async def secure_endpoint():
            return {"message": "Secure app endpoint"}

        return router

    @property
    def default_access(self) -> bool:
        return False

    @property
    def migrations_path(self) -> str:
        return "apps/secure_app/migrations"


def test_registry():
    """Test the AppRegistry functionality."""
    print("Testing AppRegistry...")

    # Get registry instance
    registry = get_registry()

    # Create test apps
    test_app = TestApp()
    secure_app = SecureApp()

    # Register apps
    registry.register(test_app)
    registry.register(secure_app)

    # Test retrieval
    assert registry.get("test_app") is test_app
    assert registry.get("secure_app") is secure_app

    # Test listing
    all_apps = registry.all()
    assert len(all_apps) >= 2
    assert test_app in all_apps
    assert secure_app in all_apps

    app_ids = registry.list_ids()
    assert "test_app" in app_ids
    assert "secure_app" in app_ids

    # Test duplicate prevention
    try:
        duplicate_app = TestApp()
        registry.register(duplicate_app)
        assert False, "Should have raised ValueError for duplicate app_id"
    except ValueError as e:
        assert "already registered" in str(e)

    # Test non-existent app
    try:
        registry.get("nonexistent")
        assert False, "Should have raised KeyError for non-existent app"
    except KeyError as e:
        assert "not registered" in str(e)

    print("✓ AppRegistry tests passed")


def test_app_properties():
    """Test that AppContract properties work correctly."""
    print("\nTesting AppContract properties...")

    test_app = TestApp()
    secure_app = SecureApp()

    # Test basic properties
    assert test_app.app_id == "test_app"
    assert test_app.display_name == "Test Application"
    assert test_app.icon == "science"
    assert test_app.default_access is True
    assert test_app.migrations_path is None

    assert secure_app.app_id == "secure_app"
    assert secure_app.display_name == "Secure Application"
    assert secure_app.icon == "lock"
    assert secure_app.default_access is False
    assert secure_app.migrations_path == "apps/secure_app/migrations"

    # Test routes
    assert isinstance(test_app.routes, APIRouter)
    assert isinstance(secure_app.routes, APIRouter)

    print("✓ AppContract properties tests passed")


if __name__ == "__main__":
    print("Running Sub-Applications Framework Tests\n")
    print("=" * 50)

    test_app_properties()
    test_registry()

    print("\n" + "=" * 50)
    print("All tests passed successfully!")
