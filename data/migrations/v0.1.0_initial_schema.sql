-- ============================================
-- Migration: v0.1.0 - Initial Schema
-- ============================================
-- Date: 2026-02-05
-- Author: Swahili NLP RAG Team
-- Description: Schema inicial com tabelas básicas do Masakhane
--              (POS, NER, News, Sentiment)

-- ============================================
-- SCHEMA VERSION TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- ============================================
-- CORE TABLES
-- ============================================

-- Terms: Vocabulário central de Swahili
CREATE TABLE IF NOT EXISTS terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    swahili_term TEXT UNIQUE NOT NULL,
    root_radical TEXT,
    noun_class TEXT DEFAULT 'N/A',
    etymology TEXT DEFAULT 'unknown',
    word_type TEXT DEFAULT 'unknown',
    is_stopword BOOLEAN DEFAULT 0,
    frequency_score REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Grammar POS: Anotações gramaticais (Masakhane-POS)
CREATE TABLE IF NOT EXISTS grammar_pos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    prefix_chain TEXT,
    sentence_id INTEGER,
    word_order INTEGER,
    confidence REAL DEFAULT 1.0,
    FOREIGN KEY (term_id) REFERENCES terms(id)
);

-- Entities: Named Entity Recognition (Masakhane-NER)
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_id INTEGER NOT NULL,
    entity_group TEXT NOT NULL,
    confidence_score REAL DEFAULT 1.0,
    FOREIGN KEY (term_id) REFERENCES terms(id)
);

-- Sentiment: Análise de sentimento
CREATE TABLE IF NOT EXISTS sentiment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_id INTEGER,
    polarity_score REAL NOT NULL,
    confidence REAL DEFAULT 1.0,
    label TEXT,
    FOREIGN KEY (term_id) REFERENCES terms(id)
);

-- News: Corpus de notícias (Masakhane-News)
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    category TEXT,
    date_published DATETIME DEFAULT CURRENT_TIMESTAMP,
    sentiment_polarity REAL,
    sentiment_confidence REAL,
    sentiment_label TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES (Performance)
-- ============================================

-- Index on terms for fast lookup
CREATE INDEX IF NOT EXISTS idx_terms_swahili 
ON terms(swahili_term);

-- Index on root for morphological queries
CREATE INDEX IF NOT EXISTS idx_terms_root 
ON terms(root_radical);

-- Index on noun class for Bantu queries
CREATE INDEX IF NOT EXISTS idx_terms_class 
ON terms(noun_class);

-- Index on POS tags
CREATE INDEX IF NOT EXISTS idx_pos_tag 
ON grammar_pos(tag);

-- Index on entity groups
CREATE INDEX IF NOT EXISTS idx_entity_group 
ON entities(entity_group);

-- Index on news category
CREATE INDEX IF NOT EXISTS idx_news_category 
ON news(category);

-- Index on news date
CREATE INDEX IF NOT EXISTS idx_news_date 
ON news(date_published);

-- ============================================
-- INSERT VERSION RECORD
-- ============================================

INSERT INTO schema_version (version, description) 
VALUES ('0.1.0', 'Initial schema with Masakhane tables (POS, NER, News, Sentiment)');

-- ============================================
-- VERIFICATION
-- ============================================

-- Verify tables were created
SELECT 'Schema v0.1.0 applied successfully!' AS status;
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;
