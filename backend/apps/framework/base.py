from abc import ABC, abstractmethod
from typing import Optional

from fastapi import APIRouter


class AppContract(ABC):
    """
    Abstract base class for Quick Controller sub-applications.

    All sub-applications must inherit from this class and implement
    the required properties to integrate with the framework.
    """

    @property
    @abstractmethod
    def app_id(self) -> str:
        """
        Unique identifier for the app (e.g., "command_center").
        Must be lowercase, alphanumeric with underscores only.
        """
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Human-readable name for the app (e.g., "Command Center").
        """
        pass

    @property
    @abstractmethod
    def icon(self) -> str:
        """
        Material Design icon name (e.g., "dashboard", "settings").
        """
        pass

    @property
    @abstractmethod
    def routes(self) -> APIRouter:
        """
        FastAPI router containing all API endpoints for this app.
        """
        pass

    @property
    def migrations_path(self) -> Optional[str]:
        """
        Optional path to app-specific database migrations.
        If None, the app has no migrations.
        """
        return None

    @property
    def default_access(self) -> bool:
        """
        If True, all authenticated users get access to this app by default.
        If False, access must be explicitly granted via user_app_permissions.
        """
        return False
