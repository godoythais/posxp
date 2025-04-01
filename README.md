# Reddit Data Pipeline com Airflow, LLM, BigQuery e Power BI

Este projeto implementa um pipeline completo de dados utilizando **Apache Airflow** para orquestração, coleta de dados do **Reddit**, classificação com **LLM (Large Language Model)**, armazenamento em **BigQuery** e visualização em **Power BI**.

## Visão Geral do Pipeline

1. **Coleta de Dados**
   - Script em Python que consome postagens do Reddit via API (utilizando `praw`).
   - Dados coletados de subreddits configuráveis (ex: `r/tecnologia`, `r/ia`, etc.).

2. **Classificação com LLM**
   - Os dados coletados são processados por um modelo de linguagem (LLM) para classificar o contexto ou intenção de cada mensagem/post.
   - Exemplos de categorias: `marca`, `sentimento`, `propósito`, `nível`, etc.

3. **Armazenamento no BigQuery**
   - Os dados classificados são enviados para uma tabela no **Google BigQuery** com os campos estruturados.
   - Suporte a logs e versionamento.

4. **Visualização com Power BI**
   - O Power BI se conecta diretamente ao BigQuery para gerar dashboards dinâmicos.
   - Possibilidade de filtro por categoria, volume por subreddit, datas, etc.

5. **Orquestração com Apache Airflow**
   - Todas as etapas são gerenciadas via DAGs no Airflow, com execução programada diariamente.
   - Logs e falhas são tratados diretamente na interface do Airflow.

## Estrutura do Projeto
```text
reddit_pipeline/ 
├── dags/ 
│ ├── reddit_collection_dag.py
│ └── reddit_to_gcp_dag.py 
├── scripts/ 
│ ├── data_collection.py 
│ └──data_classification.py 
├── conig.py
├── configs_bigquery.json
└── README.md
```
## Requisitos

- Python 3.12
- Apache Airflow (criar ambiente virtual com Python 3.10 para instalação, caso necessário)
- Google Cloud SDK (com credenciais configuradas)
- Power BI Desktop ou Power BI Service
- Bibliotecas:
  - `praw`
  - `google-cloud-bigquery`
  - `groq` (ou outro LLM provider)
  - `pandas`

## Execução

1. **Ativar ambiente virtual:**

python -m venv nome_ambiente
source nome_ambiente/bin/activate

2. **Rodar manualmente:**

python data_collection.py
python data_classification.py

3. **Rodar via Airflow:**

- Inicie o scheduler e webserver do Airflow.
- As DAGs serão executadas automaticamente conforme o agendamento configurado.

## Credenciais

Atualize o arquivo config.py com as chaves de API e credenciais necessárias:
- Reddit: client_id, client_secret, user_agent
- LLM: API_KEY
- Google Cloud: caminho do service_account.json com permissões para o BigQuery

## Observações

- O pipeline é modular e pode ser estendido para outras fontes de dados além do Reddit.
- A classificação com LLM pode ser ajustada com novos exemplos de prompt ou fine-tuning.
- Os scripts podem ser adaptados para rodar também de forma independente fora do Airflow.

