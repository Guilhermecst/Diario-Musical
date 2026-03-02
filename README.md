🎵 Diário Musical
Data Engineering & Analytics Project
1. 📌 Visão Geral do Projeto

O Diário Musical é um projeto de Data Analytics que coleta automaticamente dados pessoais de streaming do Spotify, armazena-os em um banco PostgreSQL na nuvem (Supabase) e os disponibiliza para visualização em ferramentas de BI como o Power BI.

O projeto foi desenvolvido com foco em:

Arquitetura de dados moderna

Pipeline ETL automatizado

Modelagem dimensional (Star Schema)

Execução serverless via GitHub Actions

Boas práticas de segurança (Secrets, tokens, RLS)

2. 🏗️ Arquitetura
Fluxo de Dados
Spotify API
      ↓
GitHub Actions (Scheduler)
      ↓
Python ETL
      ↓
Supabase (PostgreSQL)
      ↓
Power BI / REST API
3. 🧱 Stack Tecnológica
Camada	Tecnologia
Extração	Spotify Web API
Linguagem	Python 3.10
Orquestração	GitHub Actions
Banco de Dados	PostgreSQL (Supabase)
Driver DB	psycopg2
BI	Power BI
Controle de versão	GitHub
Segurança	GitHub Secrets
4. 🔐 Segurança

O projeto utiliza variáveis sensíveis armazenadas no GitHub Secrets:

SPOTIPY_CLIENT_ID

SPOTIPY_CLIENT_SECRET

SPOTIPY_REFRESH_TOKEN

DATABASE_URL

Nenhuma credencial é armazenada no código-fonte.

5. 🔄 Pipeline ETL
5.1 Extração

Endpoint utilizado:

GET current_user_recently_played

A extração é incremental:

Busca o MAX(played_at) do banco

Solicita apenas músicas tocadas após esse timestamp

Implementa paginação automática (limit=50)

5.2 Transformação

Durante a transformação são extraídos:

track_id

track_name

artist_id

artist_name

album_name

duration_ms

played_at

Conversões realizadas:

played_at → timestamp

Derivação futura possível:

play_date

play_hour

5.3 Carga (Load)
Estratégia de carga:

UPSERT nas dimensões

INSERT incremental na fact

Idempotência via ON CONFLICT DO NOTHING

6. 🗄️ Modelagem de Dados
Modelo Estrela (Star Schema)
🎤 dim_artist
Campo	Tipo	Descrição
artist_id	TEXT (PK)	ID Spotify
artist_name	TEXT	Nome do artista
created_at	TIMESTAMP	Data de inserção
🎵 dim_track
Campo	Tipo	Descrição
track_id	TEXT (PK)	ID Spotify
track_name	TEXT	Nome da música
album_name	TEXT	Nome do álbum
duration_ms	INTEGER	Duração
artist_id	TEXT (FK)	Referência dim_artist
📊 fact_streaming
Campo	Tipo
played_at	TIMESTAMP
track_id	TEXT
artist_id	TEXT
track_name	TEXT
artist_name	TEXT
album_name	TEXT
duration_ms	INTEGER

Primary Key:

(track_id, played_at)

Essa chave garante que cada reprodução seja única.

7. ⏰ Orquestração

O pipeline roda automaticamente via GitHub Actions:

schedule:
  - cron: "0 * * * *"

Executa a cada hora.

Também pode ser disparado manualmente (workflow_dispatch).

8. 📈 Estratégia de Atualização

O ETL é incremental:

Consulta último played_at no banco

Busca apenas novos registros

Não duplica dados

Permite reprocessamento seguro

Isso garante:

Idempotência

Eficiência

Escalabilidade

9. 🌐 Alternativas de Conexão para BI

Devido a possíveis restrições de rede (porta 5432 / IPv6), o projeto suporta duas abordagens:

Opção A — Conexão direta PostgreSQL

Power BI → PostgreSQL → Supabase

Opção B — REST API (recomendado para redes restritivas)

Power BI → HTTPS (443) → Supabase REST → PostgreSQL

10. 🚀 Próximas Evoluções Planejadas

Tabela calendário (dim_date)

Métricas pré-agregadas

API customizada

Deploy em ambiente containerizado

Dashboard público

Monitoramento de falhas do ETL

Logging estruturado

11. 📊 Exemplos de Métricas no Power BI

Total Plays

Plays por Dia

Top 10 Artistas

Top 10 Tracks

Distribuição por Hora

Tendência semanal

Média diária de reproduções

12. 🧠 Conceitos Técnicos Aplicados

OAuth 2.0 (Refresh Token Flow)

ETL incremental

UPSERT

Idempotência

Modelagem dimensional

Star Schema

Foreign Keys

Serverless orchestration

Secret management

API-first architecture

13. 🎯 Objetivo do Projeto

Demonstrar habilidades práticas em:

Engenharia de Dados

Modelagem Analítica

Automação

Cloud Database

Integração com APIs

Governança de credenciais

Estruturação de projetos reais

14. 📎 Estrutura do Repositório
src/
 ├── auth.py
 ├── extract_data.py
.github/
 └── workflows/
      └── spotify_etl.yml
requirements.txt
README.md
15. 🏁 Conclusão

O Diário Musical é um pipeline de dados completo que:

Extrai dados reais

Processa incrementalmente

Armazena de forma estruturada

Permite visualização analítica

Opera de forma automatizada

Ele simula um ambiente real de engenharia de dados em pequena escala.
