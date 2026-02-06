# Medi-Bridge SQLite Database Documentation

This document provides comprehensive information about the SQLite database schema, relationships, and usage patterns for the Medi-Bridge API.

## Table of Contents

1. [Overview](#overview)
2. [Database Schema](#database-schema)
3. [Entity Relationships](#entity-relationships)
4. [Table Definitions](#table-definitions)
5. [API Endpoints](#api-endpoints)
6. [Example Queries](#example-queries)
7. [Migration Notes](#migration-notes)

## Overview

The Medi-Bridge SQLite database stores medical conditions, exclusion methods for differential diagnosis, treatment plans, and their relationships. The database is designed to support clinical decision-making while maintaining referential integrity.

### Database Location

The SQLite database file is located at: `./data/medbridge.db`

The data directory is automatically created on first run.

### Connection Configuration

Configuration is managed via environment variables or the `Settings` class in `app/core/config.py`:

```python
SQLITE_DATABASE_PATH: str = "./data/medbridge.db"  # Database file path
SQLITE_ECHO: bool = False  # Enable SQL query logging (for debugging)
```

## Database Schema

### Entity-Relationship Diagram

```
+-------------------+          +-------------------------------+          +--------------------+
|    conditions     |          | condition_exclusion_methods   |          | exclusion_methods  |
+-------------------+          +-------------------------------+          +--------------------+
| id (PK)          |<--------| condition_id (FK)            |-------->| id (PK)           |
| name             |          | exclusion_method_id (FK) ----|          | name              |
| full_description |          | created_at                   |          | description       |
| summary          |          +-------------------------------+          | procedure_steps   |
| created_at       |                                                     | created_at        |
| updated_at       |                                                     +--------------------+
+-------------------+
         |
         |
         |
         v
+-------------------------------+
| condition_treatment_plans     |
+-------------------------------+
| id (PK)                       |
| condition_id (FK) ------------|
| treatment_plan_id (FK) -------|
| is_primary                    |
| priority                      |
| notes                         |
| created_at                    |
+-------------------------------+
                                      |
                                      |
                                      v
                            +--------------------+
                            | treatment_plans    |
                            +--------------------+
                            | id (PK)           |
                            | name              |
                            | description       |
                            | medications       |
                            | procedures        |
                            | factors           |
                            | contraindications |
                            | created_at        |
                            | updated_at        |
                            +--------------------+
```

## Entity Relationships

### Conditions and Exclusion Methods (Many-to-Many)

A medical condition can have multiple exclusion methods, and an exclusion method can apply to multiple conditions. This relationship is managed through the `condition_exclusion_methods` junction table.

- **Purpose**: Store methods to exclude similar conditions during differential diagnosis
- **Cascade**: Deleting a condition or exclusion method automatically removes associated junction records

### Conditions and Treatment Plans (Many-to-One)

A condition can have multiple associated treatment plans (for different scenarios, patient factors, etc.). Each association includes metadata like priority and whether it's the primary plan.

- **Purpose**: Associate treatment plans with conditions while maintaining clinical context
- **Design choice**: Each condition has its own treatment plan entries for clinical precision (data redundancy is acceptable)
- **Cascade**: Deleting a condition or treatment plan automatically removes associated junction records

## Table Definitions

### conditions

Stores complete medical condition information with a summary for Qdrant vector search payload.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Condition name (e.g., "Acute Appendicitis") |
| full_description | TEXT | NOT NULL | Complete condition information (long text for clinical reference) |
| summary | TEXT | NOT NULL, MAX 1000 chars | Condition summary optimized for Qdrant vector search |
| created_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT utcnow(), ON UPDATE utcnow() | Last update timestamp |

**Indexes**: Primary key on `id`

**Notes**:
- The `summary` field should be concise (<1000 chars) for optimal Qdrant payload size
- The `full_description` contains detailed clinical information

### exclusion_methods

Stores methods to exclude similar conditions during differential diagnosis.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Method name (e.g., "CT Scan Confirmation") |
| description | TEXT | NOT NULL | Method description |
| procedure_steps | TEXT | NULLABLE | JSON array of procedure steps |
| created_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT utcnow(), ON UPDATE utcnow() | Last update timestamp |

**Indexes**: Primary key on `id`

**Example `procedure_steps`**:
```json
["Perform abdominal palpation", "Check for rebound tenderness", "Order CT scan"]
```

### condition_exclusion_methods

Junction table for many-to-many relationship between conditions and exclusion methods.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| condition_id | INTEGER | NOT NULL, FOREIGN KEY → conditions.id (CASCADE) | Reference to condition |
| exclusion_method_id | INTEGER | NOT NULL, FOREIGN KEY → exclusion_methods.id (CASCADE) | Reference to exclusion method |
| created_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Record creation timestamp |

**Indexes**: Primary key on `id`, Foreign keys with CASCADE delete

### treatment_plans

Stores treatment plans including medications, procedures, and influencing factors.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Plan name (e.g., "Standard Treatment Protocol") |
| description | TEXT | NOT NULL | Plan description |
| medications | TEXT | NULLABLE | JSON array of medications |
| procedures | TEXT | NULLABLE | JSON array of procedures |
| factors | TEXT | NULLABLE | JSON array of influencing factors (age, gender, comorbidities) |
| contraindications | TEXT | NULLABLE | JSON array of contraindications |
| created_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT utcnow(), ON UPDATE utcnow() | Last update timestamp |

**Indexes**: Primary key on `id`

**Example JSON fields**:
```json
{
  "medications": ["Antibiotic A 500mg", "Pain reliever B"],
  "procedures": ["Surgical intervention", "Post-op care"],
  "factors": ["Adults 18-65", "No diabetes", "No pregnancy"],
  "contraindications": ["Allergy to penicillin", "Severe renal impairment"]
}
```

### condition_treatment_plans

Junction table for many-to-one relationship between conditions and treatment plans.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| condition_id | INTEGER | NOT NULL, FOREIGN KEY → conditions.id (CASCADE) | Reference to condition |
| treatment_plan_id | INTEGER | NOT NULL, FOREIGN KEY → treatment_plans.id (CASCADE) | Reference to treatment plan |
| is_primary | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether this is the primary plan |
| priority | INTEGER | NOT NULL, DEFAULT 0 | Priority ordering (higher = more important) |
| notes | TEXT | NULLABLE | Additional notes for this association |
| created_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Record creation timestamp |

**Indexes**: Primary key on `id`, Foreign keys with CASCADE delete

**Notes**:
- `is_primary`: Marks the default/first-line treatment option
- `priority`: Used for ordering treatment options (higher values appear first)
- Multiple treatment plans can exist for a single condition based on patient factors

## API Endpoints

All SQLite endpoints are prefixed with `/api/v1/sqlite`

### Conditions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/conditions` | Create a new condition |
| GET | `/conditions/{id}` | Get condition with relationships |
| GET | `/conditions` | List all conditions (paginated) |
| PATCH | `/conditions/{id}` | Update a condition |
| DELETE | `/conditions/{id}` | Delete a condition |

### Exclusion Methods

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/exclusion-methods` | Create a new exclusion method |
| GET | `/exclusion-methods/{id}` | Get an exclusion method |
| GET | `/exclusion-methods` | List all exclusion methods (paginated) |
| PATCH | `/exclusion-methods/{id}` | Update an exclusion method |
| DELETE | `/exclusion-methods/{id}` | Delete an exclusion method |

### Treatment Plans

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/treatment-plans` | Create a new treatment plan |
| GET | `/treatment-plans/{id}` | Get a treatment plan |
| GET | `/treatment-plans` | List all treatment plans (paginated) |
| PATCH | `/treatment-plans/{id}` | Update a treatment plan |
| DELETE | `/treatment-plans/{id}` | Delete a treatment plan |

### Associations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/conditions/{id}/exclusion-methods` | Associate exclusion method with condition |
| DELETE | `/condition-exclusion-methods/{id}` | Remove condition-exclusion method association |
| GET | `/conditions/{id}/exclusion-methods` | Get all exclusion methods for a condition |
| POST | `/conditions/{id}/treatment-plans` | Associate treatment plan with condition |
| PATCH | `/condition-treatment-plans/{id}` | Update condition-treatment plan association |
| DELETE | `/condition-treatment-plans/{id}` | Remove condition-treatment plan association |
| GET | `/conditions/{id}/treatment-plans` | Get all treatment plans for a condition |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check SQLite database health |

## Example Queries

### Using the API

#### Create a Condition

```bash
curl -X POST "http://localhost:8000/api/v1/sqlite/conditions" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acute Appendicitis",
    "full_description": "Acute inflammation of the vermiform appendix...",
    "summary": "Appendix inflammation causing right lower quadrant pain"
  }'
```

#### Get a Condition with Relationships

```bash
curl -X GET "http://localhost:8000/api/v1/sqlite/conditions/1"
```

#### Create an Exclusion Method

```bash
curl -X POST "http://localhost:8000/api/v1/sqlite/exclusion-methods" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CT Scan Confirmation",
    "description": "Use CT imaging to confirm diagnosis",
    "procedure_steps": "[\"Order CT abdomen\", \"Review radiology report\"]"
  }'
```

#### Associate Exclusion Method with Condition

```bash
curl -X POST "http://localhost:8000/api/v1/sqlite/conditions/1/exclusion-methods" \
  -H "Content-Type: application/json" \
  -d '{
    "exclusion_method_id": 1
  }'
```

#### Create a Treatment Plan

```bash
curl -X POST "http://localhost:8000/api/v1/sqlite/treatment-plans" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Standard Appendectomy Protocol",
    "description": "Standard surgical treatment for acute appendicitis",
    "medications": "[\"Ceftriaxone 2g IV\", \"Metronidazole 500mg IV\"]",
    "procedures": "[\"Laparoscopic appendectomy\", \"Post-op monitoring\"]",
    "factors": "[\"Adult patients\", \"No comorbidities\"]",
    "contraindications": "[\"Allergy to cephalosporins\"]"
  }'
```

#### Associate Treatment Plan with Condition

```bash
curl -X POST "http://localhost:8000/api/v1/sqlite/conditions/1/treatment-plans" \
  -H "Content-Type: application/json" \
  -d '{
    "treatment_plan_id": 1,
    "is_primary": true,
    "priority": 100
  }'
```

#### List Conditions with Pagination

```bash
curl -X GET "http://localhost:8000/api/v1/sqlite/conditions?skip=0&limit=10"
```

### Using Python Code

#### Direct Database Access

```python
from app.models.sqlite_db import SQLiteClientWrapper
from app.services.sqlite_crud import ConditionService

# Get a database session
async with await SQLiteClientWrapper.get_session() as session:
    # Create a condition
    condition = await ConditionService.create(session, {
        "name": "Diabetes Type 2",
        "full_description": "Chronic metabolic disorder...",
        "summary": "T2DM - insulin resistance"
    })
    print(f"Created condition: {condition.id}")
```

## Migration Notes

### Version History

- **v1.0.0** - Initial SQLite database implementation
  - Added conditions table
  - Added exclusion_methods table
  - Added condition_exclusion_methods junction table
  - Added treatment_plans table
  - Added condition_treatment_plans junction table

### Database Initialization

The database is automatically initialized on first access:

1. The `./data` directory is created if it doesn't exist
2. Database file is created at `./data/medbridge.db`
3. All tables are created with proper foreign key constraints
4. Foreign key enforcement is enabled via `PRAGMA foreign_keys = ON`

### Schema Modifications

If you need to modify the schema:

1. **Adding new columns**: Use SQLAlchemy migrations or add nullable columns with defaults
2. **Changing column types**: Export data, recreate schema, re-import data
3. **Adding new tables**: Create new model classes in `app/models/sqlite_db.py`

For production deployments, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init migrations
```

### Backup and Restore

#### Backup

```bash
cp ./data/medbridge.db ./data/medbridge.db.backup.$(date +%Y%m%d)
```

#### Restore

```bash
cp ./data/medbridge.db.backup.YYYYMMDD ./data/medbridge.db
```

### Data Export

Export data to SQL:

```bash
sqlite3 ./data/medbridge.db .dump > backup.sql
```

Import from SQL:

```bash
sqlite3 ./data/medbridge.db < backup.sql
```

## Performance Considerations

1. **Indexes**: All primary keys are automatically indexed
2. **Foreign Keys**: Enabled for referential integrity
3. **Async Operations**: Using `aiosqlite` for non-blocking database access
4. **Connection Pooling**: SQLAlchemy manages connection pooling automatically

For high-volume scenarios:
- Consider adding indexes on frequently queried columns
- Use read replicas for queries (SQLite supports this via WAL mode)
- Implement caching layer for frequently accessed data

## Troubleshooting

### Database Lock Errors

SQLite uses file-level locking. If you encounter lock errors:
- Ensure only one application instance is writing to the database
- Check for long-running transactions
- Consider using WAL mode: `PRAGMA journal_mode=WAL`

### Connection Issues

If the health check fails:
- Verify the data directory exists
- Check file permissions on the database file
- Ensure `SQLITE_DATABASE_PATH` is correctly configured

### Foreign Key Constraint Errors

Foreign key constraints are enforced. Common issues:
- Attempting to delete a record that is referenced by other records
- Creating associations with non-existent IDs

Always use the API endpoints which handle cascade deletions properly.
