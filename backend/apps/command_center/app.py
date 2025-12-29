from fastapi import APIRouter

from apps.framework.base import AppContract


class CommandCenterApp(AppContract):
    @property
    def app_id(self) -> str:
        return "command_center"

    @property
    def display_name(self) -> str:
        return "Command Center"

    @property
    def icon(self) -> str:
        return "settings"

    @property
    def routes(self) -> APIRouter:
        from apps.command_center.routes import router

        return router

    @property
    def migrations_path(self) -> str:
        return "apps/command_center/migrations"

    @property
    def default_access(self) -> bool:
        return True  # All authenticated users can access


app = CommandCenterApp()
