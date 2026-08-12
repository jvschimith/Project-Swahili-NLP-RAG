# Database Migrations

Database schema versioning system.

## 📋 Semantic Versioning

We use **Semantic Versioning** for migrations:

```
MAJOR.MINOR.PATCH

- MAJOR: Incompatible changes (breaking changes)
- MINOR: Backward-compatible feature additions
- PATCH: Bug fixes
```

## 📁 Estrutura

```
migrations/
├── v0.1.0_initial_schema.sql       # Initial schema
├── v0.2.0_add_kamusi_tables.sql    # Adds Kamusi tables
├── v0.3.0_add_indexes.sql          # Adds indexes
└── rollback/
    ├── v0.2.0_rollback.sql
    └── v0.3.0_rollback.sql
```

## 🚀 How to Apply Migrations

### Manually

```bash
# Apply migration
sqlite3 data/swahili_knowledge.db < data/migrations/v0.2.0_add_kamusi_tables.sql

# Check current version
sqlite3 data/swahili_knowledge.db "SELECT version FROM schema_version ORDER BY id DESC LIMIT 1;"
```

### Via Python

```python
from src.infrastructure.database.migrator import Migrator

migrator = Migrator()
migrator.migrate_to("0.2.0")
```

## 📝 Create a New Migration

### Template

```sql
-- Migration: v0.X.0 - Description
-- Date: YYYY-MM-DD
-- Author: Your Name
-- Description: Detailed description of the changes

-- ============================================
-- CHANGES
-- ============================================

-- 1. Create new table
CREATE TABLE IF NOT EXISTS nova_tabela (
    id INTEGER PRIMARY KEY,
    ...
);

-- 2. Add column
ALTER TABLE terms ADD COLUMN nova_coluna TEXT;

-- 3. Create index
CREATE INDEX idx_nova_coluna ON terms(nova_coluna);

-- ============================================
-- UPDATE VERSION
-- ============================================

INSERT INTO schema_version (version, description) 
VALUES ('0.X.0', 'Migration description');
```

### Rollback Template

```sql
-- Rollback: v0.X.0
-- Date: YYYY-MM-DD

-- Revert changes in reverse order

DROP INDEX IF EXISTS idx_nova_coluna;
ALTER TABLE terms DROP COLUMN nova_coluna;
DROP TABLE IF EXISTS nova_tabela;

-- Update version
DELETE FROM schema_version WHERE version = '0.X.0';
```

## 📊 Migration History

| Version | Date | Description | Status |
|--------|------|-----------|--------|
| v0.1.0 | 2026-02-04 | Initial schema (Masakhane) | ✅ Applied |
| v0.2.0 | 2026-02-05 | Adds Kamusi tables | 🔄 Pending |
| v0.3.0 | TBD | Adds performance indexes | 📋 Planned |

## ⚠️ Important Rules

1. **Never edit applied migrations** - Create a new migration instead
2. **Always create a rollback** - So changes can be reverted
3. **Test before applying** - Use a test database first
4. **Document breaking changes** - In both the commit and the file

## 🔄 Workflow

```bash
# 1. Create migration
touch data/migrations/v0.X.0_description.sql

# 2. Create rollback
touch data/migrations/rollback/v0.X.0_rollback.sql

# 3. Write SQL

# 4. Test on a test database
cp data/swahili_knowledge.db data/swahili_knowledge_test.db
sqlite3 data/swahili_knowledge_test.db < data/migrations/v0.X.0_description.sql

# 5. Verify
sqlite3 data/swahili_knowledge_test.db ".schema"

# 6. If OK, apply in production
sqlite3 data/swahili_knowledge.db < data/migrations/v0.X.0_description.sql

# 7. Commit
git add data/migrations/
git commit -m "chore(db): add migration v0.X.0 - Description"
```

## 🔍 Check the Current Schema

```bash
# View all tables
sqlite3 data/swahili_knowledge.db ".tables"

# View full schema
sqlite3 data/swahili_knowledge.db ".schema"

# View current version
sqlite3 data/swahili_knowledge.db "SELECT * FROM schema_version ORDER BY applied_at DESC LIMIT 5;"
```

## 🐛 Troubleshooting

### Migration failed

```bash
# 1. Check the error
sqlite3 data/swahili_knowledge.db ".log on"

# 2. Apply rollback
sqlite3 data/swahili_knowledge.db < data/migrations/rollback/v0.X.0_rollback.sql

# 3. Fix the migration and try again
```

### Corrupted schema

```bash
# 1. Create a backup
cp data/swahili_knowledge.db data/swahili_knowledge.db.backup

# 2. Check integrity
sqlite3 data/swahili_knowledge.db "PRAGMA integrity_check;"

# 3. If necessary, restore from the backup
```
