"""
Simple migration runner for Quick Controller.

Migrations are SQL files in the migrations/ directory named:
  001_description.sql
  002_description.sql
  etc.

Each file contains:
  -- UP
  <sql statements>

  -- DOWN
  <sql statements>
"""

import asyncio
import re
import sys
from pathlib import Path

import asyncpg

from core.config import settings

MIGRATIONS_DIR = Path(__file__).parent


async def get_connection() -> asyncpg.Connection:
    return await asyncpg.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )


async def ensure_migrations_table(conn: asyncpg.Connection) -> None:
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)


async def get_applied_migrations(conn: asyncpg.Connection) -> set[str]:
    rows = await conn.fetch("SELECT name FROM schema_migrations")
    return {row["name"] for row in rows}


def parse_migration(content: str) -> tuple[str, str]:
    """Parse migration file into up and down sections."""
    up_match = re.search(r"--\s*UP\s*\n(.*?)(?=--\s*DOWN|$)", content, re.DOTALL | re.IGNORECASE)
    down_match = re.search(r"--\s*DOWN\s*\n(.*?)$", content, re.DOTALL | re.IGNORECASE)

    up_sql = up_match.group(1).strip() if up_match else ""
    down_sql = down_match.group(1).strip() if down_match else ""

    return up_sql, down_sql


def get_migration_files() -> list[Path]:
    """Get all migration files sorted by name."""
    files = sorted(MIGRATIONS_DIR.glob("[0-9][0-9][0-9]_*.sql"))
    return files


async def migrate(direction: str = "up") -> None:
    conn = await get_connection()
    try:
        await ensure_migrations_table(conn)
        applied = await get_applied_migrations(conn)
        files = get_migration_files()

        if direction == "up":
            for file in files:
                if file.name not in applied:
                    print(f"Applying: {file.name}")
                    content = file.read_text()
                    up_sql, _ = parse_migration(content)
                    if up_sql:
                        await conn.execute(up_sql)
                        await conn.execute(
                            "INSERT INTO schema_migrations (name) VALUES ($1)", file.name
                        )
                        print(f"Applied: {file.name}")

        elif direction == "down":
            for file in reversed(files):
                if file.name in applied:
                    print(f"Reverting: {file.name}")
                    content = file.read_text()
                    _, down_sql = parse_migration(content)
                    if down_sql:
                        await conn.execute(down_sql)
                        await conn.execute(
                            "DELETE FROM schema_migrations WHERE name = $1", file.name
                        )
                        print(f"Reverted: {file.name}")
                    break  # Only revert one at a time

    finally:
        await conn.close()


async def status() -> None:
    conn = await get_connection()
    try:
        await ensure_migrations_table(conn)
        applied = await get_applied_migrations(conn)
        files = get_migration_files()

        print("Migration Status:")
        print("-" * 50)
        for file in files:
            marker = "[x]" if file.name in applied else "[ ]"
            print(f"  {marker} {file.name}")

    finally:
        await conn.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m migrations.runner <command>")
        print("Commands: up, down, status")
        sys.exit(1)

    command = sys.argv[1]

    if command == "up":
        asyncio.run(migrate("up"))
    elif command == "down":
        asyncio.run(migrate("down"))
    elif command == "status":
        asyncio.run(status())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
