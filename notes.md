# Quick Controller - Infrastructure Setup Tasks

## Development Environment
[x] Create Docker Compose configuration for local development
[x] Configure PostgreSQL container with TimescaleDB extension
[x] Configure Redis container
[x] Set up environment variables template (.env.example)

## Backend (FastAPI)
[x] Initialize Python project structure
[x] Set up FastAPI application entry point
[x] Configure asyncpg database connection pool
[x] Configure redis-py connection
[x] Create custom migration system (schema_migrations table + runner script)
[x] Write initial migration: users table

## Authentication
[x] Implement password hashing with Argon2id
[x] Create user registration endpoint (POST /api/v1/auth/register)
[x] Create login endpoint (POST /api/v1/auth/login)
[x] Implement JWT access token generation (15 min expiry)
[x] Implement refresh token with HttpOnly cookie (7 day expiry)
[x] Create token refresh endpoint (POST /api/v1/auth/refresh)
[x] Add authentication middleware/dependency for protected routes

## Frontend (Vue 3)
[x] Initialize Vue 3 project with Vite
[x] Set up Dart Sass configuration
[x] Create basic project folder structure (core/, apps/, layouts/, router/, styles/)
[x] Set up Vue Router with basic routes
[x] Create API client module for REST requests
[x] Implement authentication composable (useAuth)
[x] Build login page
[x] Build registration page
[x] Create authenticated layout wrapper

## API Foundation
[x] Define standard response envelope structure
[x] Define standard error envelope structure
[x] Create base Pydantic models for requests/responses
[x] Set up CORS configuration
[x] Add request validation middleware

## Basic Integration
[x] Connect frontend to backend authentication endpoints
[x] Implement token storage (access in memory, refresh in cookie)
[x] Add route guards for protected pages
[x] Create simple authenticated dashboard placeholder

## Master Controllers
[x] Database migration for master_controllers table
[x] Encryption module for token storage (Fernet)
[x] Discovery service with Zeroconf + hostname probing fallback
[x] HA client for REST API communication
[x] Connection manager with heartbeat monitoring
[x] API endpoints (CRUD, discover, test-connection)
[x] Frontend: ControllersView, AddControllerModal, useControllers composable
[x] Devices page with entity listing from HA
[x] Active/All entities view mode toggle

---

# Design System Planning

## Design Principles

**Philosophy:**
- Hand-crafted, no CSS frameworks (no Tailwind, Bootstrap)
- Minimal utility classes; prefer semantic component styles
- Desktop-first, flex-based layouts (mobile adaptation later, not priority)
- CSS custom properties for runtime theming
- Explicit control over every layer - no hidden magic

**UI/UX Principles:**
- Single-view focused - minimize navigation, maximize information density
- Data-dense interfaces designed for power users
- Clean visual dashboard environment
- Consistent, predictable patterns across all views
- WebSocket-first for real-time data (no polling)

**State Management Hierarchy** (prefer simpler options):
1. Component-local state (`ref()`, `reactive()`)
2. Props/emits for parent-child
3. Provide/inject for deep trees
4. Composables for reusable stateful logic
5. Dedicated store only when truly necessary

**Technical Constraints:**
- No ORM - direct SQL for full control
- No monolithic frameworks - explicit architecture
- Slim dependency footprint - only use libraries for things we shouldn't hand-roll (auth, crypto, drivers)

[ ] Define more specific interaction patterns
[ ] Define animation/motion principles
[ ] Define accessibility standards
[ ] Define information hierarchy rules

## Architecture Concept
- **Single-view focused application** - All primary interactions happen within a unified main view
- **Sub-applications system** - Modular apps that plug into the main view (future implementation)
- Focus on minimal navigation, maximum information density

## Color Palette
Main background: `#161b25`

[ ] Define primary accent color
[ ] Define secondary accent color
[ ] Define success/warning/error colors
[ ] Define text colors (primary, secondary, muted)
[ ] Define surface/card colors (elevations)
[ ] Define border colors
[ ] Create dark mode color tokens

## Typography
[x] Select primary font family (UI/headings)
[ ] Select monospace font (code, IDs, technical data)
[ ] Define type scale (sizes, weights, line-heights)
[ ] Define heading hierarchy (h1-h6)
[ ] Define body text styles

**Primary Font: Mona Sans**
- GitHub's industrial/grotesque typeface
- Variable font with weight, width, and slant axes
- 24 styles total
- Open-source (SIL Open Font License)
- Source: https://github.com/github/mona-sans

Implementation:
- Download variable font files (MonaSans.woff2, MonaSansItalic.woff2)
- Add to frontend/src/assets/fonts/
- Create @font-face declarations in styles

## Icons
[x] Select icon library

**Icon Library: Google Material Icons**
- Free to use (Apache 2.0 License)
- 2500+ icons across multiple styles
- Styles: Outlined, Rounded, Sharp, Two-tone, Filled
- Source: https://fonts.google.com/icons

Implementation options:
- Font-based: Include via Google Fonts CDN
- SVG-based: Use @material-design-icons/svg package for tree-shaking
- Recommended style: Outlined (clean, minimal, matches Mona Sans aesthetic)

## Meta Layout
[ ] Define main application shell structure
[ ] Define sidebar/navigation approach (if any)
[ ] Define header/toolbar design
[ ] Define content area constraints (max-width, padding)
[ ] Define responsive breakpoints
[ ] Define single-view container behavior

## Base Components
[ ] Button variants (primary, secondary, ghost, danger)
[ ] Input fields (text, select, checkbox, toggle)
[ ] Cards (standard, interactive, nested)
[ ] Modals/dialogs
[ ] Tooltips
[ ] Badges/pills
[ ] Loading states (spinners, skeletons)
[ ] Empty states
[ ] Status indicators (health dots, connection status)

## Spacing & Layout
[ ] Define spacing scale (4px base?)
[ ] Define grid system
[ ] Define standard gaps/margins
[ ] Define border-radius scale

## Login Page Design
Logo: `logo.png` - Minimalist "Q" with power button aesthetic (light gray #d9dce2 with black accents)

Design goals:
- Centered, focused layout against dark background (#1f2634)
- Logo prominently displayed above form
- Clean, minimal form fields
- Subtle animations on interactions
- "Quick Controller" text below logo (optional, or logo speaks for itself)

[ ] Add logo to frontend assets
[ ] Redesign login page with new branding
[ ] Redesign registration page to match
[ ] Add subtle entrance animations
[ ] Consider dark glass-morphism card for form container
