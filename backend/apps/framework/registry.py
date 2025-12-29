from typing import Dict, List

from apps.framework.base import AppContract


class AppRegistry:
    """
    Singleton registry for all sub-applications in Quick Controller.

    The registry manages app registration and lookup, ensuring no
    duplicate app IDs are registered.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._apps = {}
        return cls._instance

    def __init__(self):
        # Only initialize _apps if it doesn't exist (first instantiation)
        if not hasattr(self, "_apps"):
            self._apps: Dict[str, AppContract] = {}

    def register(self, app: AppContract) -> None:
        """
        Register a new app in the registry.

        Args:
            app: The app instance to register

        Raises:
            ValueError: If an app with the same ID is already registered
        """
        if app.app_id in self._apps:
            raise ValueError(
                f"App with ID '{app.app_id}' is already registered. "
                f"Existing: {self._apps[app.app_id].display_name}"
            )
        self._apps[app.app_id] = app

    def get(self, app_id: str) -> AppContract:
        """
        Get an app by its ID.

        Args:
            app_id: The unique app identifier

        Returns:
            The registered app instance

        Raises:
            KeyError: If no app with the given ID is registered
        """
        if app_id not in self._apps:
            raise KeyError(f"App with ID '{app_id}' is not registered")
        return self._apps[app_id]

    def all(self) -> List[AppContract]:
        """
        Get all registered apps.

        Returns:
            List of all registered app instances
        """
        return list(self._apps.values())

    def list_ids(self) -> List[str]:
        """
        Get all registered app IDs.

        Returns:
            List of all app IDs in registration order
        """
        return list(self._apps.keys())


def get_registry() -> AppRegistry:
    """
    Get the singleton AppRegistry instance.

    Returns:
        The global AppRegistry instance
    """
    return AppRegistry()
