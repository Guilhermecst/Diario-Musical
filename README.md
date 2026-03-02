# 🎵 Diário Musical

Projeto de Data Analytics utilizando a API do Spotify para construir um Data Warehouse próprio com dados de consumo musical, armazenado no Supabase (PostgreSQL) e preparado para visualização no Power BI.

---

# 📌 Objetivo do Projeto

Criar um pipeline automatizado que:

1. Extrai dados do Spotify (músicas ouvidas)
2. Processa e modela em formato dimensional (Star Schema)
3. Armazena no Supabase (PostgreSQL)
4. Permite construção de dashboards no Power BI

Foco em:

- Modelagem dimensional correta
- Boas práticas de ETL
- Automação via GitHub Actions
- Arquitetura escalável

---

# 🏗️ Arquitetura

Spotify API  
⬇  
GitHub Actions (ETL automatizado)  
⬇  
Supabase (PostgreSQL)  
⬇  
Power BI  

---

# 🔄 ETL Automatizado

O pipeline é executado automaticamente via GitHub Actions.

### Agendamento atual

Execução a cada 1 hora:

```yaml
schedule:
  - cron: "0 * * * *"
```

Também pode ser executado manualmente:

```yaml
workflow_dispatch:
```

---

# 🔐 Autenticação Spotify

Utiliza OAuth com:

- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SPOTIFY_REFRESH_TOKEN`

Secrets armazenados no GitHub.

---

# 🗄️ Modelagem de Dados (Star Schema)

## ⭐ fact_streaming

Tabela de eventos (plays).

| Coluna        | Tipo      | Descrição |
|--------------|----------|-----------|
| played_at    | TIMESTAMP | Data e hora da execução |
| track_id     | TEXT | FK para dim_track |
| artist_id    | TEXT | FK para dim_artist |
| context_type | TEXT | Origem (playlist, album, etc.) |
| context_uri  | TEXT | URI do contexto |

---

## 🎼 dim_track

| Coluna        | Tipo |
|--------------|------|
| track_id     | TEXT (PK) |
| track_name   | TEXT |
| duration_ms  | INTEGER |
| artist_id    | TEXT (FK) |
| album_id     | TEXT (FK) |
| explicit     | BOOLEAN |
| track_uri    | TEXT |

---

## 🎤 dim_artist

| Coluna       | Tipo |
|-------------|------|
| artist_id   | TEXT (PK) |
| artist_name | TEXT |
| artist_uri  | TEXT |

---

## 💿 dim_album

| Coluna                   | Tipo |
|--------------------------|------|
| album_id                 | TEXT (PK) |
| album_name               | TEXT |
| release_date             | TEXT |
| release_date_precision   | TEXT |
| total_tracks             | INTEGER |
| album_type               | TEXT |
| album_uri                | TEXT |
| album_image_url_640      | TEXT |

---

# 🔗 Relacionamentos

```
dim_artist   1 ──── N dim_track
dim_album    1 ──── N dim_track
dim_track    1 ──── N fact_streaming
```

---

# 🧠 Estratégia de Modelagem

- Fact table limpa (somente IDs + evento)
- Dimensões responsáveis por atributos descritivos
- Evita duplicação de texto
- Estrutura preparada para BI profissional

---

# 🧪 Extração Incremental

O ETL:

1. Consulta o maior `played_at` da fact
2. Busca na API apenas registros posteriores
3. Faz UPSERT nas dimensões
4. Insere novos registros na fact

Evita duplicidade via:

```sql
ON CONFLICT (track_id, played_at) DO NOTHING;
```

---

# 🚀 Tecnologias Utilizadas

- Python
- Spotipy
- PostgreSQL (Supabase)
- GitHub Actions
- Power BI

---

# 📁 Estrutura do Projeto

```
Diario-Musical
│
├── .github/workflows
│   └── spotify_etl.yml
│
├── src
│   ├── auth.py
│   ├── extract_data.py
│   ├── get_refresh_token.py
│   └── explore_vars.py
│
├── requirements.txt
└── README.md
```

---

# 📊 Próximo Passo

Construção do Dashboard no Power BI utilizando:

- Total Plays
- Distinct Tracks
- Distinct Artists
- Análise por Data
- Análise por Álbum
- Análise por Playlist (context_type)

---

# 📌 Status Atual do Projeto

✔ ETL automatizado  
✔ Modelagem dimensional implementada  
✔ Supabase configurado  
✔ Relacionamentos definidos  
⏳ Desenvolvimento do Dashboard  

---

# 🎯 Visão Final

Projeto de portfólio voltado para:

- Engenharia de Dados
- Modelagem Dimensional
- BI
- Automação
- Integração com APIs

Estrutura preparada para evoluções futuras como:

- dim_genre
- dim_playlist
- dim_date física
- Métricas avançadas (tempo escutado, tendência, etc.)