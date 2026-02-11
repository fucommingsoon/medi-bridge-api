# Medi-Bridge SQLite Database Documentation

This document provides comprehensive information about SQLite database schema, relationships, and usage patterns for Medi-Bridge API.

## Table of Contents

1. [Overview](#overview)
2. [Database Schema](#database-schema)
3. [Entity Relationships](#entity-relationships)
4. [Table Definitions](#table-definitions)
5. [API Endpoints](#api-endpoints)
6. [Example Queries](#example-queries)
7. [Migration Notes](#migration-notes)

## Overview

The Medi-Bridge SQLite database stores diseases and symptoms from the SympGAN dataset, along with doctor-patient conversations. The database is designed to support clinical decision-making while maintaining referential integrity.

### Database Location

The SQLite database file is located at: `./data/medbridge.db`

The data directory is automatically created on first run.

### Connection Configuration

Configuration is managed via environment variables or `Settings` class in `app/core/config.py`:

```python
SQLITE_DATABASE_PATH: str = "./data/medbridge.db"  # Database file path
SQLITE_ECHO: bool = False  # Enable SQL query logging (for debugging)
```

## Database Schema

### Entity-Relationship Diagram

```
+-------------------+          +-------------------------------+
|     diseases     |          | disease_symptom_associations |
+-------------------+          +-------------------------------+
| id (PK)          |<--------| disease_id (FK)            |
| cui (UNIQUE)    |          | symptom_id (FK) -------------->|
| name             |          | source                        |  symptoms
| alias            |          | created_at                   |  id (PK)        |
| definition       |          +-------------------------------+  | cui (UNIQUE)   |
| external_ids     |                                         | name            |
| created_at       |                                         | alias           |
+-------------------+                                         | definition       |
                                                             | external_ids     |
                                                             | full_description|
                                                             | summary         |
+-------------------+                                          | created_at      |
                                                          |
                                                          |
+-------------------+          +-------------------------------+
|   conversations   |          |           messages             |
+-------------------+          +-------------------------------+
| id (PK)          |<--------| conversation_id (FK) CASCADE |
| user_id          |          | id (PK)                       |
| title            |          | sent_at                       |
| started_at       |          | role                          |
| department       |          | content                       |
| patient_id       |          | created_at                    |
| progress         |          +-------------------------------+
| created_at       |
| updated_at       |
+-------------------+
```

## Entity Relationships

### Diseases and Symptoms (Many-to-Many)

A disease can have multiple associated symptoms, and a symptom can be associated with multiple diseases. This relationship is managed through the `disease_symptom_associations` junction table.

- **Purpose**: Store SympGAN dataset of disease-symptom relationships for medical knowledge reference
- **Cascade**: Deleting a disease or symptom automatically removes associated junction records
- **Data Source**: SympGAN open-source dataset (~25K diseases, ~12K symptoms, ~184K associations)

### Conversations and Messages (One-to-Many)

A conversation contains multiple messages, representing a doctor-patient consultation session.

- **Purpose**: Track consultation sessions and chat history
- **Cascade**: Deleting a conversation automatically removes all associated messages
- **Ordering**: Messages are ordered by `sent_at` timestamp (oldest first for chat history)

## Table Definitions

### diseases

Stores disease information from SympGAN dataset.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| cui | VARCHAR(50) | NOT NULL, UNIQUE, INDEX | Disease CUI (unique identifier from UMLS) |
| name | VARCHAR(500) | NOT NULL | Disease name |
| alias | TEXT | NULLABLE | Disease aliases (pipe-separated) |
| definition | TEXT | NULLABLE | Disease definition |
| external_ids | TEXT | NULLABLE | External IDs (pipe-separated, e.g., ICD10, SNOMED) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Record creation timestamp |

**Indexes**: Primary key on `id`, Unique index on `cui`

**Notes**:
- CUI (Concept Unique Identifier) is from UMLS (Unified Medical Language System)
- Contains approximately 25,000 diseases from SympGAN dataset

### symptoms

Stores symptom information from SympGAN dataset, extended with rich content fields.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| cui | VARCHAR(50) | NOT NULL, UNIQUE, INDEX | Symptom CUI (unique identifier from UMLS) |
| name | VARCHAR(500) | NOT NULL | Symptom name |
| alias | TEXT | NULLABLE | Symptom aliases (pipe-separated) |
| definition | TEXT | NULLABLE | Symptom definition |
| external_ids | TEXT | NULLABLE | External IDs (pipe-separated) |
| full_description | TEXT | NULLABLE | Complete symptom information (long text for clinical reference) |
| summary | TEXT | NULLABLE | Symptom summary (optimized for vector search payload) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Record creation timestamp |

**Indexes**: Primary key on `id`, Unique index on `cui`

**Notes**:
- Extended with `full_description` and `summary` fields for rich content beyond SympGAN data
- Contains approximately 12,000 symptoms from SympGAN dataset

### disease_symptom_associations

Junction table for many-to-many relationship between diseases and symptoms from SympGAN dataset.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| disease_id | INTEGER | NOT NULL, FOREIGN KEY → diseases.id (CASCADE), INDEX | Reference to disease |
| symptom_id | INTEGER | NOT NULL, FOREIGN KEY → symptoms.id (CASCADE), INDEX | Reference to symptom |
| source | VARCHAR(200) | NULLABLE | Data source (e.g., HSDN, MalaCards, OrphaNet) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Record creation timestamp |

**Indexes**: Primary key on `id`, Foreign keys with CASCADE delete, Index on `disease_id`, Index on `symptom_id`

**Notes**:
- Contains approximately 184,000 disease-symptom associations
- Source field indicates origin of the association (HSDN, MalaCards, OrphaNet, UMLS, etc.)

### conversations

Records doctor-patient conversation sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| user_id | INTEGER | NULLABLE | Current logged-in user ID (reserved for future use) |
| title | VARCHAR(255) | NOT NULL | Conversation title/subject |
| started_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Session start time |
| department | VARCHAR(100) | NULLABLE | Department/Category (e.g., "Emergency", "Internal Medicine") |
| patient_id | INTEGER | NULLABLE | Patient ID (reserved for future use) |
| progress | TEXT | NULLABLE | Current progress (JSON array of condition IDs from last vector search) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT utcnow(), ON UPDATE utcnow() | Last update timestamp |

**Indexes**: Primary key on `id`

**Example `progress`**:
```json
[1, 5, 12, 23]
```

### messages

Records individual messages within a conversation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| conversation_id | INTEGER | NOT NULL, FOREIGN KEY → conversations.id (CASCADE) | Reference to conversation |
| sent_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Message send time |
| role | VARCHAR(50) | NULLABLE | Message role (reserved for speaker identification via voice analysis) |
| content | TEXT | NOT NULL | Message content (text) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT utcnow() | Record creation timestamp |

**Indexes**: Primary key on `id`, Foreign key with CASCADE delete

**Notes**:
- `role` field is reserved for future use when speaker identification is implemented
- Messages are typically ordered by `sent_at` in ascending order for chat history display

## API Endpoints

All SQLite endpoints are prefixed with `/api/v1/sqlite`

### Diseases

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/diseases` | Create a new disease |
| GET | `/diseases/{id}` | Get disease with symptoms |
| GET | `/diseases` | List all diseases (paginated) |
| GET | `/diseases/search/{query}` | Search diseases by name |
| PATCH | `/diseases/{id}` | Update a disease |
| DELETE | `/diseases/{id}` | Delete a disease |

### Symptoms

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/symptoms` | Create a new symptom |
| GET | `/symptoms/{id}` | Get symptom with diseases |
| GET | `/symptoms` | List all symptoms (paginated) |
| GET | `/symptoms/search/{query}` | Search symptoms by name |
| PATCH | `/symptoms/{id}` | Update a symptom |
| DELETE | `/symptoms/{id}` | Delete a symptom |

### Disease-Symptom Associations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/disease-symptom-associations` | Associate a disease with a symptom |
| GET | `/diseases/{id}/symptoms` | Get all symptoms for a disease |
| GET | `/symptoms/{id}/diseases` | Get all diseases for a symptom |

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/conversations` | Create a new conversation |
| GET | `/conversations/{id}` | Get conversation with messages |
| GET | `/conversations` | List all conversations (paginated, most recent first) |
| PATCH | `/conversations/{id}` | Update a conversation |
| DELETE | `/conversations/{id}` | Delete a conversation (and all messages) |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/messages` | Create a new message |
| GET | `/messages/{id}` | Get a message |
| GET | `/conversations/{id}/messages` | List all messages in a conversation (paginated, oldest first) |
| PATCH | `/messages/{id}` | Update a message |
| DELETE | `/messages/{id}` | Delete a message |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check SQLite database health |

## Example Queries

### Using the API

#### Create a Disease

```bash
curl -X POST "http://localhost:8000/api/v1/sqlite/diseases" \
  -H "Content-Type: application/json" \
  -d '{
    "cui": "C0001234",
    "name": "Type 2 Diabetes",
    "alias": "T2DM|Adult-onset diabetes",
    "definition": "A metabolic disorder characterized by high blood sugar..."
  }'
```

#### Create a Symptom

```bash
curl -X POST "http://localhost:8000/api/v1/sqlite/symptoms" \
  -H "Content-Type: application/json" \
  -d '{
    "cui": "C0027834",
    "name": "Chest pain",
    "alias": "Thoracic pain|Chest discomfort",
    "definition": "Pain or discomfort in the chest area...",
    "full_description": "Detailed clinical description of chest pain symptoms...",
    "summary": "Chest discomfort or pain"
  }'
```

#### Create a Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/sqlite/conversations" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Patient with abdominal pain",
    "department": "Emergency"
  }'
```

#### Add a Message to Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/sqlite/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "content": "Patient presents with severe right lower quadrant pain"
  }'
```

#### Get Conversation with Messages

```bash
curl -X GET "http://localhost:8000/api/v1/sqlite/conversations/1"
```

#### Update Conversation Progress

```bash
curl -X PATCH "http://localhost:8000/api/v1/sqlite/conversations/1" \
  -H "Content-Type: application/json" \
  -d '{
    "progress": "[1, 5, 12]"
  }'
```

#### List Conversations

```bash
curl -X GET "http://localhost:8000/api/v1/sqlite/conversations?skip=0&limit=10"
```

#### Get Conversation Messages

```bash
curl -X GET "http://localhost:8000/api/v1/sqlite/conversations/1/messages?skip=0&limit=50"
```

#### Get Symptoms for a Disease

```bash
curl -X GET "http://localhost:8000/api/v1/sqlite/diseases/1/symptoms"
```

#### Search Diseases

```bash
curl -X GET "http://localhost:8000/api/v1/sqlite/diseases/search/diabetes"
```

#### Search Symptoms

```bash
curl -X GET "http://localhost:8000/api/v1/sqlite/symptoms/search/fever"
```

#### Get Diseases for a Symptom

```bash
curl -X GET "http://localhost:8000/api/v1/sqlite/symptoms/1/diseases"
```

### Using Python Code

#### Direct Database Access

```python
from app.models.sqlite_db import SQLiteClientWrapper
from app.services.sqlite_crud import (
    DiseaseService,
    SymptomService,
    DiseaseSymptomAssociationService,
    ConversationService,
    MessageService,
)

# Get a database session
async with await SQLiteClientWrapper.get_session() as session:
    # Create a disease
    disease = await DiseaseService.create(session, {
        "cui": "C0001234",
        "name": "Type 2 Diabetes",
        "alias": "T2DM",
        "definition": "Metabolic disorder...",
        "external_ids": "ICD10:E11"
    })
    print(f"Created disease: {disease.id}")

    # Create a symptom with extended fields
    symptom = await SymptomService.create(session, {
        "cui": "C0027834",
        "name": "Chest pain",
        "full_description": "Pain or discomfort in the chest area...",
        "summary": "Chest discomfort"
    })
    print(f"Created symptom: {symptom.id}")

    # Create disease-symptom association
    from app.schemas.sqlite import DiseaseSymptomAssociationCreate

    association = await DiseaseSymptomAssociationService.create_association(
        session,
        DiseaseSymptomAssociationCreate(
            disease_id=disease.id,
            symptom_id=symptom.id,
            source="HSDN"
        )
    )
    print(f"Created association: {association.id}")

    # Create a conversation
    conversation = await ConversationService.create(session, {
        "title": "Diabetes follow-up",
        "department": "Endocrinology"
    })
    print(f"Created conversation: {conversation.id}")

    # Add a message
    message = await MessageService.create(session, {
        "conversation_id": conversation.id,
        "content": "Patient reports blood sugar levels"
    })
    print(f"Created message: {message.id}")

    # Get disease with symptoms
    disease_with_symptoms = await DiseaseService.get_with_symptoms(session, disease.id)
    print(f"Disease {disease.name} has {len(disease_with_symptoms.symptom_associations)} symptoms")

    # Search diseases
    diseases = await DiseaseService.search_by_name(session, "diabetes", limit=10)
    print(f"Found {len(diseases)} diseases matching 'diabetes'")
```

## Migration Notes

### Version History

- **v1.0.0** - Initial SQLite database implementation
  - Added diseases table (SympGAN dataset)
  - Added symptoms table (SympGAN dataset, extended)
  - Added disease_symptom_associations table (SympGAN relationships)
  - Added conversations table
  - Added messages table
  - Added one-to-many relationship between conversations and messages

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
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
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
- Consider adding indexes on frequently queried columns (cui indexes already present)
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

- Verify the `data` directory exists
- Check file permissions on the database file
- Ensure `SQLITE_DATABASE_PATH` is correctly configured

### Foreign Key Constraint Errors

Foreign key constraints are enforced. Common issues:

- Attempting to delete a record that is referenced by other records
- Creating associations with non-existent IDs
- Always use API endpoints which handle cascade deletions properly
