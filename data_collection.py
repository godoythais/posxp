import praw 
import json
import pandas as pd 
from google.cloud import bigquery
from config import client_id, client_secret, user_agent

CREDENTIALS_PATH = "/home/google_credencials.json"

PROJECT_ID = "posxp"
DATASET_ID = "reddit_data"
TABLE_ID = "table-name"

client = bigquery.Client.from_service_account_json(CREDENTIALS_PATH)

reddit = praw.Reddit(
    client_id,
    client_secret,
    user_agent
)

SUBREDDIT_NAME = "running"
SEARCH_TERM = ["Nike vs Adidas", "best running shoes", "running shoes", "best running for beginners", "waterproof running shoes"]
LIMIT = 1500

subreddit = reddit.subreddit(SUBREDDIT_NAME)
posts = subreddit.search(SEARCH_TERM, sort="new", limit=LIMIT)

data = []
for post in posts:
    data.append({
        "Título": post.title,
        "Autor": post.author.name if post.author else "Desconhecido",
        "URL": post.url,
        "Data": post.created_utc,
        "Upvotes": post.score,
        "Comentários": post.num_comments,
        "Texto": post.selftext
    })

OUTPUT_JSON_FILE = "reddit_search_results.json"
with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"Resultados filtrados e salvos em {OUTPUT_JSON_FILE}!")

df = pd.DataFrame(data)
df["Data"] = pd.to_datetime(df["Data"], unit="s")

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Salvar os dados no BigQuery
job = client.load_table_from_dataframe(df, table_ref)
job.result()

print(f" {len(df)} posts carregados no BigQuery: {table_ref}")

query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}` LIMIT 5"
df_bq = client.query(query).to_dataframe()
print(df_bq.head())