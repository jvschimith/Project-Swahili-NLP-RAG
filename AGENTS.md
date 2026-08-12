# Swahili Linguistic Intelligence API

## 🧠 Project Overview

This project is a **linguistic knowledge infrastructure for Swahili**, not a generic NLP API.

The goal is to:

- Ingest real Swahili text (news, articles, etc.)
- Analyze linguistic structure (morphology, lexemes, context)
- Build structured knowledge
- Provide an API for querying language understanding

This system should behave as a **linguistic knowledge engine**, not a chatbot or simple translator.

---

## 🚫 What This Project Is NOT

- NOT a chatbot
- NOT a generic RAG system
- NOT just a translation API
- NOT just sentiment analysis

---

## 🎯 Core Domain Model (IMPORTANT)

The system is based on linguistic ontology.

### Central concepts:

- **Lexeme** → abstract semantic unit (core concept)
- **WordForm** → surface realization of a lexeme
- **Meaning** → semantic interpretation
- **Context** → real-world usage (sentences)
- **Derivation** → relation between lexemes
- **MorphologicalAnalysis** → internal structure of words

### ⚠️ Critical Rule

Avoid modeling everything as a single "term".

Prefer:

- Lexeme + WordForm separation

---

## 🧬 Morphology (CRITICAL COMPONENT)

The project already includes an advanced morphology engine:

- EnhancedRootExtractor
- ParadigmGenerator
- MorphologicalFeatureExtractor

### Rules:

- ALWAYS reuse existing morphology modules
- DO NOT replace them with simple regex or generic NLP
- DO NOT simplify morphology logic

Swahili is an **agglutinative language**, and morphology is the core value of the system.

---

## 🌍 Language Constraints

- Primary language: Swahili
- Translation direction: Swahili → English
- All API outputs must be in English

---

## ⚙️ Architecture

The system has two main layers:

### 1. Ingestion Pipeline (async)
- Text ingestion
- Linguistic analysis
- Knowledge extraction
- Data storage

### 2. API Layer (sync)
- FastAPI
- Query-based responses
- Low latency

---

## 🗄️ Data Modeling Guidelines

When modifying models:

- Keep entities small and focused
- Separate structure from meaning
- Avoid duplication across forms

### Prefer:

- Lexeme → central entity
- WordForm → variations
- Context → usage
- Meaning → semantic layer

---

## 🔌 API Design Rules

All endpoints must:

- Return structured data (not raw text)
- Include linguistic explanations when possible
- Avoid hallucinated responses

### Key endpoints:

- `/word/{lemma}` → lexical query
- `/analyze` → morphological analysis
- `/translate` → contextual translation
- `/search` → semantic search

---

## 🧪 Development Rules

### When modifying code:

- Make incremental changes
- Do not rewrite large modules without explanation
- Prefer adapting existing logic over creating new ones
- Keep compatibility with existing code when possible

---

## 🔍 Refactoring Guidelines

When refactoring:

1. Do NOT break working features
2. Introduce new structures gradually
3. Create compatibility layers if needed
4. Explain changes before applying them

---

## 🚨 Critical Constraints

- Do NOT replace domain logic with generic AI shortcuts
- Do NOT remove morphology modules
- Do NOT collapse Lexeme and WordForm into one entity
- Do NOT introduce unnecessary abstractions

---

## 🧠 Expected Behavior from Agent

When asked to implement something:

1. First understand the linguistic requirement
2. Then map it to existing domain structures
3. Reuse existing modules whenever possible
4. Only create new code if necessary

---

## 📊 Priority Order

When making decisions, prioritize:

1. Linguistic correctness
2. Domain consistency
3. Code reuse
4. Performance
5. Simplicity

---

## 🧪 Validation

After changes:

- Ensure API still runs
- Validate morphology outputs
- Ensure no duplication of linguistic data
- Verify consistency between lexeme and forms

---

## 🧠 Final Principle

This system models a **language**, not just text.

Every implementation decision must respect:

→ linguistic structure  
→ semantic coherence  
→ real-world usage  

