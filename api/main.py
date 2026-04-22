from fastapi import FastAPI
import json

app = FastAPI()

def load_data():
    with open("../wired_articles.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/articles")
def get_articles():
    return load_data()