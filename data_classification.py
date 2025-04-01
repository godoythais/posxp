import requests
import json
from langdetect import detect 
from config import GROQ_API_KEY, URL
from google.cloud import bigquery
import pandas as pd

CREDENTIALS_PATH = "/home/google_credencials.json"

PROJECT_ID = "posxp"
DATASET_ID = "reddit_data"
TABLE_ID = "table-name"

client = bigquery.Client.from_service_account_json(CREDENTIALS_PATH)

def verify_language(text):
    try:
        idiom = detect(text)
        return idiom == "en"
    except:
        return False

def limit_text(text, limit=300):
    return text[:limit] + "..." if len(text) > limit else text

def classify_text(text):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    prompt = {
        "role": "system",
        "content": (
            "Analyze the following text about running shoes and classify it:\n"
            f'Text: "{text}"\n\n'
            "Recommended brand: Nike, Adidas, Asics, Other brand. Write just name of brand.\n"
            "Runner level: Beginner, Amateur, Professional, or Undefined.\n"
            "Shoe purpose: Marathon, Training, Speed, Casual, or Other.\n"
            "Main evaluation aspect: Comfort, Durability, Performance, Price, or Other.\n"
            "Respond in the format: Brand | Level | Purpose | Aspect.\n"
            "Respond with only one word per category, example: Nike | Amateur | Marathon | Comfort."
        )
    }
    
    data = {"model": "llama3-8b-8192", "messages": [prompt], "temperature": 0.7}
    
    response = requests.post(URL, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return "error"
    
with open("reddit_search_results.json", "r", encoding="utf-8") as file:
    data = json.load(file)

for item in data:
    text = item.get("Texto", "").strip()

    if not text:
        print(f"Skipping empty text for post: {item.get('Título', 'Título Desconhecido')}")
        continue  

    if not verify_language(text):
        print(f"Skipping non-English text: {item.get('Título', 'Título Desconhecido')}")
        continue

    text_optimized = limit_text(text)
    classification = classify_text(text_optimized)

    print(f"LLM Response: {classification}")

    parts = classification.split(" | ")
    if len(parts) == 4:
        item["Brand"], item["Level"], item["Purpose"], item["Aspect"] = parts

with open("classified_results.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"Classification completed and saved in classified_results.json!")

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
