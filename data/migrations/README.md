# Database Migrations

Sistema de versionamento de schema do banco de dados.

## 📋 Versionamento Semântico

Usamos **Semantic Versioning** para migrations:

```
MAJOR.MINOR.PATCH

- MAJOR: Mudanças incompatíveis (breaking changes)
- MINOR: Adição de funcionalidades compatíveis
- PATCH: Correções de bugs
```

## 📁 Estrutura

```
migrations/
├── v0.1.0_initial_schema.sql       # Schema inicial
├── v0.2.0_add_kamusi_tables.sql    # Adiciona tabelas Kamusi
├── v0.3.0_add_indexes.sql          # Adiciona índices
└── rollback/
    ├── v0.2.0_rollback.sql
    └── v0.3.0_rollback.sql
```

## 🚀 Como Aplicar Migrations

### Manualmente

```bash
# Aplicar migration
sqlite3 data/swahili_knowledge.db < data/migrations/v0.2.0_add_kamusi_tables.sql

# Verificar versão atual
sqlite3 data/swahili_knowledge.db "SELECT version FROM schema_version ORDER BY id DESC LIMIT 1;"
```

### Via Python

```python
from src.infrastructure.database.migrator import Migrator

migrator = Migrator()
migrator.migrate_to("0.2.0")
```

## 📝 Criar Nova Migration

### Template

```sql
-- Migration: v0.X.0 - Descrição
-- Date: YYYY-MM-DD
-- Author: Seu Nome
-- Description: Descrição detalhada das mudanças

-- ============================================
-- MUDANÇAS
-- ============================================

-- 1. Criar nova tabela
CREATE TABLE IF NOT EXISTS nova_tabela (
    id INTEGER PRIMARY KEY,
    ...
);

-- 2. Adicionar coluna
ALTER TABLE terms ADD COLUMN nova_coluna TEXT;

-- 3. Criar índice
CREATE INDEX idx_nova_coluna ON terms(nova_coluna);

-- ============================================
-- ATUALIZAR VERSÃO
-- ============================================

INSERT INTO schema_version (version, description) 
VALUES ('0.X.0', 'Descrição da migration');
```

### Rollback Template

```sql
-- Rollback: v0.X.0
-- Date: YYYY-MM-DD

-- Reverter mudanças na ordem inversa

DROP INDEX IF EXISTS idx_nova_coluna;
ALTER TABLE terms DROP COLUMN nova_coluna;
DROP TABLE IF EXISTS nova_tabela;

-- Atualizar versão
DELETE FROM schema_version WHERE version = '0.X.0';
```

## 📊 Histórico de Migrations

| Versão | Data | Descrição | Status |
|--------|------|-----------|--------|
| v0.1.0 | 2026-02-04 | Schema inicial (Masakhane) | ✅ Applied |
| v0.2.0 | 2026-02-05 | Adiciona tabelas Kamusi | 🔄 Pending |
| v0.3.0 | TBD | Adiciona índices de performance | 📋 Planned |

## ⚠️ Regras Importantes

1. **Nunca edite migrations aplicadas** - Crie uma nova migration
2. **Sempre crie rollback** - Para poder reverter mudanças
3. **Teste antes de aplicar** - Use banco de teste primeiro
4. **Documente breaking changes** - No commit e no arquivo

## 🔄 Workflow

```bash
# 1. Criar migration
touch data/migrations/v0.X.0_descricao.sql

# 2. Criar rollback
touch data/migrations/rollback/v0.X.0_rollback.sql

# 3. Escrever SQL

# 4. Testar em banco de teste
cp data/swahili_knowledge.db data/swahili_knowledge_test.db
sqlite3 data/swahili_knowledge_test.db < data/migrations/v0.X.0_descricao.sql

# 5. Verificar
sqlite3 data/swahili_knowledge_test.db ".schema"

# 6. Se OK, aplicar em produção
sqlite3 data/swahili_knowledge.db < data/migrations/v0.X.0_descricao.sql

# 7. Commit
git add data/migrations/
git commit -m "chore(db): add migration v0.X.0 - Descrição"
```

## 🔍 Verificar Schema Atual

```bash
# Ver todas as tabelas
sqlite3 data/swahili_knowledge.db ".tables"

# Ver schema completo
sqlite3 data/swahili_knowledge.db ".schema"

# Ver versão atual
sqlite3 data/swahili_knowledge.db "SELECT * FROM schema_version ORDER BY applied_at DESC LIMIT 5;"
```

## 🐛 Troubleshooting

### Migration falhou

```bash
# 1. Verificar erro
sqlite3 data/swahili_knowledge.db ".log on"

# 2. Aplicar rollback
sqlite3 data/swahili_knowledge.db < data/migrations/rollback/v0.X.0_rollback.sql

# 3. Corrigir migration e tentar novamente
```

### Schema corrompido

```bash
# 1. Fazer backup
cp data/swahili_knowledge.db data/swahili_knowledge.db.backup

# 2. Verificar integridade
sqlite3 data/swahili_knowledge.db "PRAGMA integrity_check;"

# 3. Se necessário, reconstruir do backup
```
