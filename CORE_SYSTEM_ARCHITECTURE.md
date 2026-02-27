# Core System Architecture Documentation

This document provides a framework-agnostic technical reference for the core foundational modules and reusable infrastructure of the CMS. It is designed to allow for full system reconstruction in any backend stack (Node.js, Laravel, Go, etc.) by detailing the logic, data flow, and architectural patterns.

---

## 1. Architectural Overview

The system follows a strict **Model-View-Controller (MVC)** architecture with a clear separation between data persistence, business logic, and presentation.

### Core Design Principles

1.  **SQL Abstraction Layer**: All data access is mediated through a base model that handles common CRUD operations and provides a hook for automated metadata injection.
2.  **Audit Trail Enforcement**: Every table in the system (except for metadata/lookup tables) must include: `id`, `created_by`, `created_at`, `updated_by`, `updated_at`.
3.  **Automated Metadata**: The system automatically captures the current user ID and timestamp on every `INSERT` and `UPDATE` operation.
4.  **Service Layer Orchestration**: Controllers should not contain business logic. Instead, they calls "Services" which handle validation, cross-module synchronization (e.g., Google Sheets), and complex workflows.

---

## 2. Core Services & Shared Infrastructure

### Base Model (Data Access Layer)

The `BaseModel` provides an abstraction over SQL (currently SQLite). It implements:

- **Generic Indexing**: Supports dynamic filtering (including date ranges), search across multiple fields, multi-column sorting, and pagination.
- **Join Resolution**: Automatically joins with the `users` table to resolve `created_by` and `updated_by` IDs into human-readable names.
- **Table Aliasing**: Uses table aliases (e.g., `t` for target table) to prevent field ambiguity during complex joins.

### Base Service Layer

A generic service layer that wraps the `BaseModel` methods. It standardizes the interface between Controllers and Models, allowing for easy addition of global middleware (logging, validation) across all modules.

### Session Management

The session is implemented as a **Singleton** with an **Observer pattern**.

- **Persistence**: Current user state is persisted to a local JSON file (`session.json`), allowing the application to maintain state across restarts.
- **Expiration**: Sessions include an `expires_at` timestamp. If the current time exceeds this value, the session is cleared, forcing re-authentication.
- **UI Sync**: Views subscribe to session changes. When permissions or user status change, the session notifies all registered observers to refresh the UI (e.g., hiding/showing menu items).

---

## 3. Authentication System

### Login Flow

1.  **Credential Retrieval**: Fetch user by `username`.
2.  **Account Status Check**: Verify `account_status` is 'active' and `is_locked` is false.
3.  **Password Verification**:
    - **Hashing**: Uses `bcrypt` for password verification.
    - **Legacy Migration**: Supports plaintext checks for legacy accounts. If a plaintext check succeeds, the system automatically hashes the password using `bcrypt` and updates the database record.
4.  **Last Login Tracking**: Updates `last_login` timestamp in the database upon successful entry.
5.  **External Validation (Optional)**: If `spreadsheet_validation` is enabled for the user, a secondary check is performed against an external source (Google Sheets) to ensure the account remains valid in the master registry.

### Security Constraints

- **Internal State**: Authentication state is maintained in-memory (Singleton) and validated against the `session.json` on boot.
- **Encryption**: All passwords stored must be `bcrypt` hashed strings.

---

## 4. Account Management

### User Structure

Users are defined by:

- `id` (Internal PK)
- `customId` (Public identifier, e.g., Employee ID)
- `username` / `password` (Authentication)
- `access_level` (FK to RBAC system)
- `account_status` ('active', 'inactive', 'pending')
- `is_locked` (Boolean toggle for security lockouts)

### Logic & Constraints

- **Registration**: Requires validation of unique `username` and `customId`.
- **Password Management**: Passwords can be updated at any time; the service layer ensures new passwords are hashed before storage.
- **Soft Deletion**: While the system supports `destroy`, the recommended pattern is to set `account_status` to 'disabled' or 'inactive' to preserve audit integrity.

---

## 5. Role-Based Access Control (RBAC)

### Permission Model

Permissions are defined at the **Access Level** (Role) level. Each role contains a mapping of **Navigation IDs** to specific capabilities:

- `view`: Visibility of the module.
- `add`: Ability to create records.
- `edit`: Ability to modify records.
- `delete`: Ability to remove records.
- `export`: Ability to pull data into CSV/Excel.
- `import`: Ability to bulk upload data.

### Resolution Flow

1.  **Role Retrieval**: Logged-in user's `access_level` ID is checked.
2.  **Permission String**: Permissions are stored as Comma-Separated Values (CSV) of Navigation IDs in the `access_levels` table.
3.  **Policy Enforcement**:
    - **Controller Level**: Before any action (store, edit, update), the application verifies if the current navigation's ID exists within the user's role permission string.
    - **UI Level**: Buttons (e.g., "Add New", "Edit") are dynamically enabled/disabled based on this same resolution logic.

---

## 6. Generic CRUD Builder System

The system includes a meta-programming engine to generate complete software modules from simple definitions.

### Architecture

- **Metadata**: `crud_definitions` table stores field names, types (text, number, dropdown, date), and visibility settings.
- **Code Generation**: Uses **Jinja2 templates** to emit:
  - `Model`: Inherits from `BaseModel`, defines specific joins.
  - `Service`: Standard wrapper for the model.
  - `Controller`: Implementation of index, create, store, edit, update, and destroy actions.
  - `Migration`: A standalone SQL script to create the physical table.
- **Registration**: Automatically inserts a record into the `navigations` table, making the module immediately visible to the RBAC system.

### Extensibility & Schema Synchronization

- **Non-Destructive Sync**: If a module definition is updated (e.g., a new field added), the service layer uses `ALTER TABLE` to sync the database schema without losing existing data.
- **Automatic Audit Fields**: Every generated table is automatically provisioned with the standard audit fields (`created_at`, etc.).

---

## 7. Global Settings / Configuration

### Storage Structure

Settings are stored in a dedicated `settings` table as Key-Value pairs.

- `setting_name`: Unique key (slug).
- `setting_value`: The current value.
- `setting_options`: JSON array of allowed values (used to populate dropdowns in the UI).

### Access Patterns

- **Runtime Usage**: Settings are fetched via the `SettingsService` whenever needed (e.g., app name, theme, API keys).
- **Caching**: While currently DB-driven, the service layer is designed to support an in-memory dictionary cache to reduce SQL overhead for frequently accessed configuration keys.
