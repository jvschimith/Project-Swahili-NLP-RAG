# Data Raw Directory

Este diretório contém os **dados brutos** (raw data) das fontes externas.

## 📁 Estrutura

```
raw/
├── masakhane-pos/     # Part-of-Speech tagging data
├── masakhane-ner/     # Named Entity Recognition data
├── masakhane-news/    # News corpus
└── kamusi/            # Kamusi dictionary files
```

## 📥 Como Obter os Dados

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

## ⚠️ Importante

- Estes arquivos são rastreados pelo **Git LFS** (Large File Storage)
- Não commite arquivos muito grandes sem LFS configurado
- Use `git lfs track "*.csv"` se adicionar novos tipos de arquivo

## 📊 Estatísticas dos Dados

| Dataset | Linhas | Tamanho | Descrição |
|---------|--------|---------|-----------|
| POS Test | ~1.000 | ~50KB | Anotações gramaticais |
| NER Test | ~1.000 | ~50KB | Entidades nomeadas |
| News Test | ~1.000 | ~500KB | Corpus de notícias |
| Kamusi CSV | 16.683 | ~2MB | Dicionário completo |

## 🔄 Atualização dos Dados

Para atualizar os dados das fontes originais:

```bash
bash scripts/download_data.sh
```

## 📝 Formato dos Dados

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
