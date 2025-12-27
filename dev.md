# Quick Controller — Development & Architecture Document

**Version:** 0.1.0  
**Last Updated:** December 2025  
**Status:** Initial Design Phase

---

## 1. Project Overview

Quick Controller is an IoT meta-analysis platform that provides a cloud-based intelligence and unification layer on top of HomeAssistant-powered device ecosystems. Rather than replacing HomeAssistant, Quick Controller treats HomeAssistant instances as managed data sources, enabling centralized multi-tenant device management, historical data analysis, real-time monitoring, and modular domain-specific applications.

### 1.1 Core Value Proposition

The platform bridges the gap between raw IoT infrastructure and actionable business/consumer insights by providing:

- Centralized management of one or more HomeAssistant instances per user account
- Historical data persistence beyond HomeAssistant's native capabilities
- A modular application framework where domain-specific tools operate over shared device data
- Real-time alerting engine with multi-channel notification delivery
- Clean visual dashboard environment accessible from any device

### 1.2 Deployment Models

Quick Controller supports two primary deployment contexts:

| Model | Description |
|-------|-------------|
| **Managed (B2B)** | We provision and configure the HomeAssistant environment for the client. Full vertical integration from hardware to cloud dashboard. |
| **Self-Service (B2C)** | Users sign up and connect their existing HomeAssistant instance. Platform handles discovery, authentication, and integration. |

The architecture must accommodate both models without divergent codepaths.

---

## 2. Technology Stack

### 2.1 Core Technologies

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | Vue 3 (Composition API, Vanilla JS) | Lightweight, reactive, excellent TypeScript optional support. No build-time framework overhead. |
| **Styling** | Dart Sass | Native compilation, actively maintained, faster than node-sass. |
| **Backend API** | FastAPI (Python) | Async-native, WebSocket support, automatic OpenAPI generation, minimal boilerplate. |
| **Relational Database** | PostgreSQL | Mature, performant, handles complex relational queries for app state and user data. |
| **Time-Series Database** | TimescaleDB | PostgreSQL extension for time-series workloads. Keeps us in one database ecosystem while optimizing for IoT telemetry patterns. |
| **Message Broker / Cache** | Redis | Pub/sub for real-time event fan-out, caching layer, session storage. |
| **Containerization** | Docker / Docker Compose | Consistent environments across development and production. |

### 2.2 What We're Intentionally Not Using

| Avoided | Reason |
|---------|--------|
| **ORM (SQLAlchemy, etc.)** | Direct SQL provides full control, clearer performance characteristics, and avoids abstraction leakage. We maintain our own migration system. |
| **Heavy State Management (Vuex/Pinia)** | Vue 3's Composition API with reactive refs and provide/inject handles most state needs. Introduce dedicated stores only when prop drilling becomes genuinely painful. |
| **Monolithic Frameworks** | No Django, no Nuxt. We want explicit control over every layer without hidden magic. |

### 2.3 Approved External Dependencies

While maintaining a slim dependency footprint, certain functionality should never be hand-rolled:

- **Authentication primitives:** JWT encoding/decoding, password hashing (argon2/bcrypt)
- **WebSocket protocol handling:** Use established libraries for frame management and connection lifecycle
- **Cryptographic operations:** Never implement custom encryption
- **Database drivers:** asyncpg for PostgreSQL, redis-py for Redis

---

## 3. Database Architecture

### 3.1 Dual-Store Strategy

Quick Controller employs a dual-database architecture reflecting two fundamentally different data access patterns:

**PostgreSQL (Application State)**
- User accounts, authentication, sessions
- Device registry and metadata
- App configurations and user preferences
- Subscription tiers and permissions
- Alert rule definitions
- Audit logs

**TimescaleDB (Telemetry)**
- Sensor readings and state changes
- High-frequency time-series data
- Automatic data retention policies
- Time-bucketed aggregations

TimescaleDB runs as a PostgreSQL extension, meaning both databases share connection infrastructure and query language. This simplifies operations compared to running a separate InfluxDB instance.

### 3.2 Schema Design Principles

**Naming Conventions:**
- Tables: `snake_case`, plural (e.g., `users`, `devices`, `sensor_readings`)
- Columns: `snake_case`
- Primary keys: `id` (UUID preferred for distributed safety)
- Foreign keys: `{referenced_table_singular}_id`
- Timestamps: `created_at`, `updated_at`, always UTC

**Multi-Tenancy:**
- All tenant-scoped tables include a `user_id` or `organization_id` foreign key
- Queries must always filter by tenant context; enforce at the repository layer
- Consider row-level security policies in PostgreSQL for defense-in-depth

**App-Specific Tables:**
- Each modular app may define its own tables
- Prefix with app namespace: `greenhouse_zones`, `greenhouse_schedules`
- Apps must never directly query another app's namespaced tables

### 3.3 Time-Series Data Model

Sensor telemetry flows into a hypertable partitioned by time:

```
sensor_readings
├── time (TIMESTAMPTZ, primary dimension)
├── device_id (UUID, foreign key)
├── entity_id (VARCHAR, HomeAssistant entity identifier)
├── state (VARCHAR, raw state value)
├── attributes (JSONB, additional entity attributes)
└── ingested_at (TIMESTAMPTZ, when Quick Controller received it)
```

TimescaleDB continuous aggregates pre-compute common rollups (hourly averages, daily min/max) to accelerate dashboard queries.

### 3.4 Migration Strategy

We maintain a custom migration system rather than using Alembic or similar tools. Migrations are:

- Sequential SQL files: `001_initial_schema.sql`, `002_add_alerts_table.sql`
- Stored in `migrations/` directory
- Tracked via a `schema_migrations` table recording applied migration identifiers and timestamps
- Applied via a simple Python runner script that executes pending migrations in order
- Always reversible: each migration file includes both `up` and `down` sections

---

## 4. HomeAssistant Integration

### 4.1 Connection Architecture

HomeAssistant instances connect outbound to Quick Controller, avoiding NAT traversal complexity. The connection flow:

```
┌─────────────────────┐         ┌─────────────────────┐
│   HomeAssistant     │         │   Quick Controller  │
│   (Customer Site)   │         │      (Cloud)        │
│                     │         │                     │
│  ┌───────────────┐  │         │  ┌───────────────┐  │
│  │ QC Integration│──┼────────►│  │ HA Gateway    │  │
│  │    Addon      │  │   WSS   │  │   Service     │  │
│  └───────────────┘  │         │  └───────────────┘  │
│                     │         │                     │
└─────────────────────┘         └─────────────────────┘
```

### 4.2 Pairing Flow

1. User generates a **pairing token** from the Quick Controller dashboard
2. Token is entered into the HomeAssistant integration (custom component or addon)
3. HomeAssistant integration initiates WSS connection to Quick Controller
4. Quick Controller validates token, associates connection with user account
5. Token is exchanged for rotating credentials used for ongoing authentication
6. Connection established; real-time data streaming begins

### 4.3 Data Ingestion

The HomeAssistant integration subscribes to state change events and forwards them to Quick Controller:

**Streamed Events:**
- `state_changed`: Entity state updates (sensors, switches, etc.)
- `entity_registry_updated`: Device/entity metadata changes
- `homeassistant_started` / `homeassistant_stopped`: Instance lifecycle

**Polling (Fallback):**
- Full state snapshot on initial connection
- Periodic reconciliation every N minutes to catch missed events

### 4.4 Configuration Push

Quick Controller can push configuration back to HomeAssistant instances:

- Automation rules generated by alert definitions
- Entity visibility/naming preferences
- Integration-specific settings

This uses HomeAssistant's REST API authenticated via long-lived access tokens stored (encrypted) in Quick Controller's database.

### 4.5 Connection Lifecycle Management

| State | Description | Platform Behavior |
|-------|-------------|-------------------|
| **Connected** | Active WSS connection, data flowing | Normal operation |
| **Reconnecting** | Connection dropped, attempting reestablishment | Buffer incoming data, exponential backoff on retries |
| **Offline** | Reconnection failed after threshold | Mark instance offline, alert user, stop buffering |
| **Paused** | User-initiated disconnection | Ignore instance until resumed |

Connection status is exposed via the user dashboard and factored into alerting logic (don't alert on sensor thresholds if the instance is offline).

---

## 5. Real-Time Infrastructure

### 5.1 WebSocket Architecture

Quick Controller is WebSocket-first for all dashboard interactions. Polling is not used for live data.

**Client Connection Flow:**
1. Client authenticates via REST, receives JWT
2. Client opens WSS connection to `/ws/connect`
3. Server validates JWT, associates connection with user session
4. Client subscribes to channels (devices, apps, alerts)
5. Server pushes events matching subscriptions

### 5.2 Pub/Sub Fan-Out Model

Redis pub/sub handles message distribution between backend processes and connected clients:

```
┌──────────────┐      ┌─────────┐      ┌──────────────┐
│ HA Gateway   │─────►│  Redis  │─────►│ WS Handler 1 │───► Client A
│   Service    │      │ Pub/Sub │      └──────────────┘
└──────────────┘      │         │      ┌──────────────┐
                      │         │─────►│ WS Handler 2 │───► Client B
                      └─────────┘      └──────────────┘
                                                       ───► Client C
```

**Channel Naming Convention:**
- `user:{user_id}:devices` — All device updates for a user
- `user:{user_id}:device:{device_id}` — Specific device updates
- `user:{user_id}:alerts` — Alert triggers and resolutions
- `user:{user_id}:app:{app_id}` — App-specific events

### 5.3 Message Envelope Format

All WebSocket messages follow a consistent envelope:

```json
{
  "type": "device.state_changed",
  "timestamp": "2024-12-15T10:30:00Z",
  "payload": {
    "device_id": "uuid",
    "entity_id": "sensor.temperature",
    "state": "72.5",
    "attributes": {}
  }
}
```

**Reserved Type Prefixes:**
- `device.*` — Device and entity events
- `alert.*` — Alert lifecycle events
- `app.*` — App-specific events
- `system.*` — Platform-level notifications (maintenance, errors)

### 5.4 Scaling Considerations

Initial architecture handles moderate scale with single Redis instance. Future scaling path:

- Redis Cluster for horizontal pub/sub scaling
- Sticky sessions or connection registry for targeted messaging
- Consider NATS or Kafka if message replay/persistence becomes necessary

---

## 6. Modular Application Architecture

### 6.1 Three-Tier Structure

```
┌─────────────────────────────────────────────────────────┐
│                    Individual Apps                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Greenhouse  │  │  Industrial │  │   Energy    │ ... │
│  │  Monitor    │  │   Tracker   │  │  Dashboard  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│                  App Framework Layer                     │
│  • App registration and lifecycle                        │
│  • Standard contracts for device access                  │
│  • Permission enforcement                                │
│  • UI mounting and routing                               │
├─────────────────────────────────────────────────────────┤
│                  Core Platform Layer                     │
│  • Authentication / Authorization                        │
│  • Device registry and HomeAssistant connection          │
│  • Data ingestion pipelines                              │
│  • WebSocket infrastructure                              │
│  • Alerting engine                                       │
└─────────────────────────────────────────────────────────┘
```

### 6.2 App Contract

Each app must implement a standard interface declaring its requirements and capabilities:

**Backend (Python module):**
- `app_id`: Unique identifier
- `display_name`: Human-readable name
- `required_device_types`: List of device types the app operates on
- `routes`: FastAPI router to mount under `/api/apps/{app_id}/`
- `event_handlers`: Functions to invoke on relevant platform events
- `migrations`: App-specific database migrations

**Frontend (Vue module):**
- `app_id`: Must match backend
- `routes`: Vue Router routes to mount under `/app/{app_id}/`
- `components`: Exported components for embedding in shared contexts
- `subscriptions`: WebSocket channels the app needs

### 6.3 App Isolation Rules

- Apps must not import from other apps' modules
- Cross-app data access goes through platform APIs only
- App-specific database tables use namespaced prefixes
- Apps cannot modify core platform tables directly
- Apps receive device data through platform-provided interfaces, never direct HomeAssistant access

### 6.4 Permission Model

App access is controlled at the user/organization level:

| Permission Level | Access |
|------------------|--------|
| **Disabled** | App not visible, routes return 403 |
| **Read-Only** | Can view app data, cannot modify configurations |
| **Full Access** | Complete app functionality |

Permissions tie into subscription tiers—certain apps may be premium features.

---

## 7. API Design

### 7.1 REST Conventions

**Base URL:** `/api/v1/`

**Resource Naming:**
- Plural nouns: `/devices`, `/alerts`, `/users`
- Nested resources where ownership is clear: `/devices/{id}/readings`
- App-scoped routes: `/apps/{app_id}/...`

**HTTP Methods:**
- `GET`: Retrieve resource(s)
- `POST`: Create resource
- `PUT`: Full resource replacement
- `PATCH`: Partial update
- `DELETE`: Remove resource

**Response Envelope:**

```json
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

**Error Envelope:**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable message",
    "details": { ... }
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

### 7.2 Authentication

**Token Flow:**
1. Client POSTs credentials to `/api/v1/auth/login`
2. Server returns access token (short-lived, ~15 min) and refresh token (longer-lived, ~7 days)
3. Access token passed via `Authorization: Bearer {token}` header
4. Refresh token used to obtain new access tokens without re-authentication

**Token Storage:**
- Access token: Memory only (JavaScript variable), never localStorage
- Refresh token: HttpOnly secure cookie

### 7.3 Query Patterns for Time-Series

Time-series endpoints accept standardized query parameters:

| Parameter | Description |
|-----------|-------------|
| `start` | ISO8601 timestamp, beginning of range |
| `end` | ISO8601 timestamp, end of range |
| `resolution` | Aggregation bucket: `raw`, `1m`, `5m`, `1h`, `1d` |
| `aggregation` | Function: `avg`, `min`, `max`, `sum`, `count` |

Example: `GET /api/v1/devices/{id}/readings?start=2024-12-01&end=2024-12-15&resolution=1h&aggregation=avg`

### 7.4 AI Integration Readiness

API design assumes AI agents as first-class consumers:

- Consistent, predictable response structures
- Descriptive error messages that explain what went wrong
- Idempotent operations where possible (safe to retry)
- Comprehensive OpenAPI schema auto-generated by FastAPI
- Semantic operation names that map to natural language intents

---

## 8. Alerting Engine

### 8.1 Alert Anatomy

An alert definition consists of:

- **Trigger Condition**: Expression evaluated against incoming device data
- **Evaluation Window**: Time period over which condition is assessed
- **Severity**: `info`, `warning`, `critical`
- **Notification Channels**: Where to send alerts (email, SMS, push, webhook)
- **Cooldown Period**: Minimum time between repeated alerts for same condition
- **Escalation Rules**: What happens if alert isn't acknowledged

### 8.2 Condition Types

| Type | Description | Example |
|------|-------------|---------|
| **Threshold** | Value crosses boundary | Temperature > 100°F |
| **Rate of Change** | Value changing too fast | Pressure dropping > 5 psi/min |
| **Absence** | Expected data not received | No reading for 10 minutes |
| **Pattern** | Sequence of states | Door opened 3+ times in 1 hour |
| **Compound** | Multiple conditions combined | Temp > 100 AND humidity > 80% |

### 8.3 Processing Pipeline

```
Device Event
    │
    ▼
┌─────────────────┐
│ Event Ingestion │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Alert Evaluator │────►│ Active Alerts   │
└────────┬────────┘     │    Registry     │
         │              └─────────────────┘
         ▼ (trigger)
┌─────────────────┐
│  Notification   │
│   Dispatcher    │
└────────┬────────┘
         │
         ▼
┌────┬────┬────┬────┐
│Email│SMS│Push│Hook│
└────┴────┴────┴────┘
```

### 8.4 Notification Channels

| Channel | Implementation |
|---------|----------------|
| **Email** | Transactional email service (SendGrid, Postmark, or SES) |
| **SMS** | Twilio or similar |
| **Push** | Firebase Cloud Messaging for mobile apps |
| **Webhook** | User-configured HTTP endpoints |
| **In-App** | WebSocket push to connected clients |

---

## 9. Frontend Architecture

### 9.1 Project Structure

```
src/
├── core/                    # Platform-level code
│   ├── api/                 # API client, request handling
│   ├── auth/                # Authentication state, guards
│   ├── components/          # Shared UI components
│   ├── composables/         # Reusable composition functions
│   ├── websocket/           # WebSocket client, subscription management
│   └── utils/               # Helpers, formatters
├── apps/                    # Modular applications
│   ├── greenhouse/
│   │   ├── components/
│   │   ├── views/
│   │   ├── composables/
│   │   └── index.js         # App registration
│   └── energy/
│       └── ...
├── layouts/                 # Page layout wrappers
├── router/                  # Vue Router configuration
├── styles/                  # Global Sass, variables, mixins
└── main.js                  # Application entry point
```

### 9.2 State Management Strategy

**Hierarchy of Approaches (prefer earlier options):**

1. **Component-local state**: `ref()` and `reactive()` for UI state that doesn't leave the component
2. **Props/emits**: Parent-child communication
3. **Provide/inject**: Deep component trees needing shared context
4. **Composables**: Reusable stateful logic (e.g., `useDevices()`, `useAlerts()`)
5. **Dedicated store**: Only when multiple unrelated components need synchronized access to the same mutable state

### 9.3 WebSocket Integration

A core composable manages the WebSocket lifecycle:

- Establishes connection on authentication
- Handles reconnection with exponential backoff
- Provides subscription API for components to request specific channels
- Exposes reactive state for connection status
- Dispatches incoming messages to registered handlers

Components subscribe declaratively and receive updates reactively without managing connection details.

### 9.4 Styling Architecture

**Dart Sass Configuration:**
- Global variables in `styles/_variables.scss` (colors, spacing, breakpoints)
- Mixins in `styles/_mixins.scss`
- Base/reset styles in `styles/_base.scss`
- Component styles scoped via `<style lang="scss" scoped>`

**Principles:**
- Mobile-first responsive design
- CSS custom properties for runtime theming
- Minimal utility classes; prefer semantic component styles
- No CSS framework (no Tailwind, Bootstrap); hand-crafted styles

---

## 10. Security Considerations

### 10.1 Authentication Security

- Passwords hashed with Argon2id (memory-hard, resistant to GPU attacks)
- JWT access tokens short-lived (15 minutes maximum)
- Refresh tokens rotated on use (one-time use)
- Failed login rate limiting per IP and per account
- Optional MFA (TOTP-based)

### 10.2 Data Security

- All external traffic over TLS 1.3
- Database connections encrypted
- Sensitive configuration values encrypted at rest (HomeAssistant tokens, notification credentials)
- User data isolated via tenant ID on all queries; row-level security as defense-in-depth

### 10.3 API Security

- CORS restricted to known frontend origins
- CSRF protection for cookie-based authentication
- Input validation on all endpoints (Pydantic models in FastAPI)
- Rate limiting on public endpoints
- Request size limits to prevent payload attacks

### 10.4 HomeAssistant Connection Security

- Pairing tokens single-use and time-limited (24 hour expiry)
- Long-lived access tokens encrypted in database
- WebSocket connections require valid session
- Instance identity verified on each reconnection

---

## 11. Deployment Architecture

### 11.1 Container Topology

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   nginx     │  │   FastAPI   │  │   FastAPI   │     │
│  │  (reverse   │  │  (API +     │  │  (HA        │     │
│  │   proxy)    │  │   WS)       │  │  Gateway)   │     │
│  └──────┬──────┘  └─────────────┘  └─────────────┘     │
│         │                                               │
│         │         ┌─────────────┐  ┌─────────────┐     │
│         │         │ PostgreSQL  │  │    Redis    │     │
│         │         │ + Timescale │  │             │     │
│         │         └─────────────┘  └─────────────┘     │
│         │                                               │
│         └──► Static files (Vue build)                  │
└─────────────────────────────────────────────────────────┘
```

### 11.2 Service Responsibilities

| Service | Role |
|---------|------|
| **nginx** | TLS termination, static file serving, reverse proxy to API |
| **API** | REST endpoints, WebSocket connections for clients |
| **HA Gateway** | Manages connections to HomeAssistant instances, data ingestion |
| **PostgreSQL + TimescaleDB** | Persistent data storage |
| **Redis** | Pub/sub message broker, caching, session storage |

### 11.3 Environment Configuration

Configuration via environment variables, organized by concern:

- `QC_DATABASE_URL`: PostgreSQL connection string
- `QC_REDIS_URL`: Redis connection string
- `QC_JWT_SECRET`: Secret for JWT signing
- `QC_ENCRYPTION_KEY`: Key for encrypting sensitive stored data
- `QC_HA_GATEWAY_URL`: Internal URL for HA Gateway service
- `QC_SMTP_*`: Email configuration
- `QC_TWILIO_*`: SMS configuration

### 11.4 Development Environment

Docker Compose provides local development parity:

- Hot-reloading for both frontend (Vite) and backend (uvicorn --reload)
- Local PostgreSQL and Redis instances
- Volume mounts for code changes without rebuild
- Seed data scripts for consistent development state

---

## 12. Testing Strategy

### 12.1 Backend Testing

| Layer | Approach |
|-------|----------|
| **Unit** | Pure functions, business logic, isolated from I/O |
| **Integration** | API endpoints with test database, Redis |
| **Contract** | WebSocket message format validation |

Test database uses same schema, reset between test runs. Avoid mocking database queries; test against real PostgreSQL.

### 12.2 Frontend Testing

| Layer | Approach |
|-------|----------|
| **Unit** | Composables, utility functions |
| **Component** | Individual components with Vue Test Utils |
| **Integration** | Critical user flows with Playwright |

### 12.3 HomeAssistant Integration Testing

Mock HomeAssistant server that implements relevant API surface:
- Simulates WebSocket connection and state change events
- Allows scripted scenarios (connection drops, malformed data, high throughput)
- Used in both automated tests and manual QA

---

## 13. Development Workflow

### 13.1 Branch Strategy

- `main`: Production-ready code, deployed automatically
- `develop`: Integration branch, deployed to staging
- `feature/*`: Feature development, merged to develop via PR
- `hotfix/*`: Production fixes, merged to both main and develop

### 13.2 Code Review Requirements

- All changes via pull request
- Minimum one approval required
- CI checks must pass (tests, linting)
- No direct pushes to main or develop

### 13.3 CI Pipeline

1. **Lint**: Python (ruff), JavaScript (ESLint), Sass (stylelint)
2. **Test**: Full test suite with coverage reporting
3. **Build**: Docker image construction
4. **Security**: Dependency vulnerability scanning
5. **Deploy**: Automatic deployment on merge (staging for develop, production for main)

---

## 14. Future Considerations

Items explicitly out of scope for initial release but architecturally accommodated:

- **Mobile Applications**: API and WebSocket infrastructure supports native clients
- **Multi-Organization Accounts**: Data model supports organization-level tenancy
- **Horizontal Scaling**: Stateless API servers, Redis Cluster, read replicas
- **Self-Hosted Option**: Container architecture enables customer deployment
- **Plugin Marketplace**: App framework designed for third-party extensions
- **Advanced AI Features**: Data accessibility and API consistency support future ML/LLM integration

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Device** | A physical IoT device registered in Quick Controller |
| **Entity** | A HomeAssistant entity (sensor, switch, etc.) belonging to a device |
| **Instance** | A HomeAssistant installation connected to Quick Controller |
| **App** | A modular sub-application within the Quick Controller platform |
| **Tenant** | A user or organization account; the boundary for data isolation |

---

## Appendix B: Key Decisions Log

| Decision | Rationale | Date |
|----------|-----------|------|
| TimescaleDB over InfluxDB | Keeps us in PostgreSQL ecosystem, simpler operations | Dec 2025 |
| No ORM | Direct SQL control, avoid abstraction overhead | Dec 2025 |
| Redis pub/sub for fan-out | Simple, sufficient for initial scale, clear upgrade path | Dec 2025 |
| Outbound HA connections | Avoids NAT traversal, customer doesn't need to open ports | Dec 2025 |
| Vue 3 Composition API | Lightweight, flexible, avoids framework lock-in | Dec 2025 |
| Custom migration system | Full control, no magic, matches slim philosophy | Dec 2025 |

---

*This document is the authoritative reference for Quick Controller's architecture. Update it as decisions evolve.*