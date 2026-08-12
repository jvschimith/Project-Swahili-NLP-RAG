# Data Raw Directory

This directory contains the **raw data** from external sources.

## 📁 Estrutura

```
raw/
├── masakhane-pos/     # Part-of-Speech tagging data
├── masakhane-ner/     # Named Entity Recognition data
├── masakhane-news/    # News corpus
└── kamusi/            # Kamusi dictionary files
```

## 📥 How to Obtain the Data

### Masakhane POS

```bash
cd data/raw/masakhane-pos
wget https://raw.githubusercontent.com/masakhane-io/masakhane-pos/main/data/swa/test.txt -O pos_swa_test.txt
```

### Masakhane NER

```bash
cd data/raw/masakhane-ner
wget https://raw.githubusercontent.com/masakhane-io/masakhane-ner/main/data/swa/test.txt -O ner_swa_test.txt
```

### Masakhane News

```bash
cd data/raw/masakhane-news
wget https://raw.githubusercontent.com/masakhane-io/masakhane-news/main/data/swa/test.tsv -O news_swa_test.tsv
```

### Kamusi Dictionary

```bash
cd data/raw/kamusi
wget https://raw.githubusercontent.com/Kalebu/kamusi/main/words.csv
wget https://raw.githubusercontent.com/Kalebu/kamusi/main/words.json
```

## ⚠️ Important

- These files are tracked with **Git LFS** (Large File Storage)
- Do not commit very large files without Git LFS configured
- Use `git lfs track "*.csv"` if you add new file types

## 📊 Data Statistics

| Dataset | Rows | Size | Description |
|---------|--------|---------|-----------|
| POS Test | ~1,000 | ~50KB | Grammatical annotations |
| NER Test | ~1,000 | ~50KB | Named entities |
| News Test | ~1,000 | ~500KB | News corpus |
| Kamusi CSV | 16,683 | ~2MB | Full dictionary |

## 🔄 Data Updates

To update the data from the original sources:

```bash
bash scripts/download_data.sh
```

## 📝 Data Format

### POS (CoNLL Format)

```
Zanzibar	PROPN
ni	AUX
kisiwa	NOUN
...
```

### NER (BIO Format)

```
Zanzibar	B-LOC
ni	O
kisiwa	O
...
```

### News (TSV)

```
category	headline	text	url
Kitaifa	Rais...	...	https://...
```

### Kamusi (CSV)

```
word,meaning,synonyms,english
mtu,binadamu,watu,person
...
```
