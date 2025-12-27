# Quick Controller - Claude Code Configuration

## Project Overview

Quick Controller is an IoT meta-analysis platform that provides a cloud-based intelligence layer on top of HomeAssistant-powered device ecosystems. This project uses a modern full-stack architecture with FastAPI backend and Vue 3 frontend.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python), asyncpg, PostgreSQL + TimescaleDB |
| Frontend | Vue 3 (Composition API), Vite, Dart Sass |
| Cache/Pubsub | Redis |
| Infrastructure | Docker Compose |
| Testing | Playwright (E2E) |

## Project Structure

```
quickcontroller.com/
├── backend/           # FastAPI application
│   ├── api/v1/        # API routes
│   ├── core/          # Config, security, dependencies
│   ├── db/            # Database connections
│   ├── migrations/    # SQL migrations
│   └── main.py        # App entry point
├── frontend/          # Vue 3 application
│   └── src/
│       ├── core/      # API client, composables
│       ├── views/     # Page components
│       ├── layouts/   # Layout wrappers
│       ├── router/    # Vue Router
│       └── styles/    # Sass files
├── tests/e2e/         # Playwright E2E tests
└── docker-compose.yml # All services
```

## Development Workflow

### For Feature Requests and Bug Fixes

When the user requests a new feature or bug fix, follow this workflow:

1. **Delegate to `full-stack-engineer`** for implementation
   - The full-stack-engineer handles all coding tasks
   - It understands the codebase patterns and conventions
   - It creates necessary migrations, API endpoints, and frontend components

2. **After implementation, delegate to `testing-engineer`** for verification
   - Run the full E2E test suite
   - Analyze any failures
   - Report results back

3. **If tests fail**, coordinate fixes:
   - testing-engineer reports specific failures
   - full-stack-engineer implements fixes
   - testing-engineer re-runs tests
   - Repeat until all tests pass

### Example Workflow

```
User: "Add a forgot password feature"

1. → Invoke full-stack-engineer to implement:
   - Backend: password reset endpoints, email sending
   - Frontend: forgot password form, reset form
   - Database: password reset tokens table

2. → Invoke testing-engineer to verify:
   - Run: docker compose run --rm e2e
   - Check for regressions
   - Create new tests for the feature if needed

3. → Report results to user
```

## Key Commands

```bash
# Start all services
docker compose up -d

# Run database migrations
docker exec qc-api python -m migrations.runner up

# Run E2E tests
docker compose run --rm e2e

# View logs
docker compose logs -f api
docker compose logs -f frontend
```

## Code Conventions

### Backend (Python/FastAPI)
- Use `get_pool().acquire()` for database operations (not direct pool import)
- Follow existing patterns in `api/v1/` for new endpoints
- Create migrations in `migrations/` with format `NNN_description.sql`
- Use Pydantic models for request/response validation

### Frontend (Vue 3)
- Use Composition API with `<script setup>`
- Create composables in `core/composables/` for shared state
- Use Sass variables from `styles/_variables.scss`
- Follow existing component patterns in `views/`

### Database
- Tables use snake_case, plural names
- Primary keys are UUIDs
- Always include `created_at` and `updated_at` timestamps
- Foreign keys follow `{table_singular}_id` pattern

## Testing Requirements

All features must pass E2E tests before completion. The testing-engineer agent is responsible for:
- Running the full test suite after changes
- Creating new tests for new features
- Ensuring no regressions are introduced

## Architecture Reference

For detailed architecture decisions, see `dev.md`.
