# 🎵 Diário Musical  

Pipeline de Engenharia de Dados para coleta e armazenamento automático do histórico de reprodução do Spotify.

---

## 📌 Sobre o Projeto

O **Diário Musical** é um projeto de Data Engineering que extrai automaticamente os dados de músicas reproduzidas na conta pessoal do Spotify, processa essas informações via Python e armazena em um banco PostgreSQL hospedado no Supabase.

O pipeline roda de forma automatizada através do GitHub Actions, garantindo atualização contínua dos dados sem necessidade de execução manual.

---

## 🏗️ Arquitetura Implementada

```
Spotify Web API
        ↓
GitHub Actions (agendamento automático)
        ↓
Python ETL
        ↓
Supabase (PostgreSQL)
```

---

## 🧱 Stack Tecnológica

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.10 |
| API | Spotify Web API |
| Banco de Dados | PostgreSQL (Supabase) |
| Orquestração | GitHub Actions |
| Driver DB | psycopg2 |
| Autenticação | OAuth 2.0 (Refresh Token Flow) |

---

## 🔐 Segurança

As credenciais são armazenadas como **GitHub Secrets**, garantindo que nenhuma informação sensível seja versionada.

Secrets utilizados:

- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`
- `SPOTIPY_REFRESH_TOKEN`
- `DATABASE_URL`

---

## 🔄 Pipeline ETL

### 🔹 Extração

A extração utiliza o endpoint:

```python
sp.current_user_recently_played()
```

A coleta é **incremental**, baseada no último `played_at` armazenado no banco:

```sql
SELECT MAX(played_at) FROM fact_streaming;
```

Somente novas reproduções são buscadas.

---

### 🔹 Transformação

Os dados são organizados e estruturados com os seguintes campos:

- `track_id`
- `track_name`
- `artist_id`
- `artist_name`
- `album_name`
- `duration_ms`
- `played_at`

O campo `played_at` é convertido para timestamp para garantir consistência no banco.

---

### 🔹 Carga

A carga é dividida em duas etapas:

#### 1️⃣ UPSERT nas dimensões

##### `dim_artist`

```sql
PRIMARY KEY (artist_id)
```

##### `dim_track`

```sql
PRIMARY KEY (track_id)
```

Atualização feita via:

```sql
ON CONFLICT DO UPDATE
```

---

#### 2️⃣ Inserção incremental na fact

Tabela:

### `fact_streaming`

```sql
PRIMARY KEY (track_id, played_at)
```

Estratégia:

```sql
ON CONFLICT (track_id, played_at) DO NOTHING
```

Isso garante:

- Idempotência
- Nenhuma duplicação de dados
- Segurança em reprocessamentos

---

## 🗄️ Modelagem de Dados

O projeto utiliza modelo estrela simplificado.

### 🎤 dim_artist

| Campo | Tipo |
|--------|------|
| artist_id | TEXT |
| artist_name | TEXT |
| created_at | TIMESTAMP |

---

### 🎵 dim_track

| Campo | Tipo |
|--------|------|
| track_id | TEXT |
| track_name | TEXT |
| album_name | TEXT |
| duration_ms | INTEGER |
| artist_id | TEXT |

---

### 📊 fact_streaming

| Campo | Tipo |
|--------|------|
| played_at | TIMESTAMP |
| track_id | TEXT |
| artist_id | TEXT |
| track_name | TEXT |
| artist_name | TEXT |
| album_name | TEXT |
| duration_ms | INTEGER |

---

## ⏰ Orquestração

O workflow está configurado para execução automática via GitHub Actions.

Trecho do `spotify_etl.yml`:

```yaml
on:
  schedule:
    - cron: "0 * * * *"  # Executa a cada hora (UTC)
  workflow_dispatch:
```

O pipeline pode ser executado:

- Automaticamente (agendado)
- Manualmente via interface do GitHub

---

## 📂 Estrutura do Repositório

```
src/
 ├── auth.py
 ├── extract_data.py

.github/
 └── workflows/
      └── spotify_etl.yml

requirements.txt
README.md
```

---

## 🧠 Conceitos Aplicados

- OAuth 2.0 (Refresh Token Flow)
- ETL incremental
- UPSERT
- Idempotência
- Modelagem Dimensional
- Star Schema
- Automação em nuvem
- Gestão de Secrets
- Conexão segura com PostgreSQL

---

## 🎯 Objetivo do Projeto

Demonstrar na prática:

- Integração com APIs externas
- Construção de pipeline automatizado
- Modelagem analítica
- Persistência de dados em nuvem
- Boas práticas de engenharia de dados

---

## 🏁 Status Atual

- ✔ Extração incremental implementada  
- ✔ Banco PostgreSQL estruturado  
- ✔ Modelagem dimensional aplicada  
- ✔ GitHub Actions automatizado  
- ✔ Conexão validada com Supabase  