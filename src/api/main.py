from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import uvicorn
import feedparser
import numpy as np

app = FastAPI()
MODEL_PATH = "upasanapandey/news-classifier"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# Pipelines
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
ner = pipeline("ner", grouped_entities=True)  # uses default model

labels = ["World", "Sports", "Business", "Sci/Tech"]  # AG News mapping

class Query(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "News Recommendation API running!"}
    
@app.post("/predict")
def predict(q: Query):
    inputs = tokenizer(q.text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        out = model(**inputs)
        probs = torch.nn.functional.softmax(out.logits, dim=-1).squeeze()

    label_index = int(torch.argmax(out.logits))
    # Convert probabilities to Python floats for JSON serialization
    probs_list = [float(p) for p in probs]

    return {
        "label": labels[label_index],
        "probs": probs_list
    }


@app.post("/analyze")
def analyze(q: Query):
    pred = predict(q)

    # --- summarization with error handling
    try:
        text = q.text[:1000]
        summary_result = summarizer(text, max_length=120, min_length=30, do_sample=False)
        summary = summary_result[0]["summary_text"] if summary_result else "No summary generated."
    except Exception as e:
        summary = f"⚠️ Summarization failed: {str(e)}"

    # --- NER with cleaning and deduplication
    try:
        entities_raw = ner(q.text)
    except Exception as e:
        entities_raw = [{"entity_group": "Error", "word": str(e)}]

    seen = set()
    entities = []
    for ent in entities_raw:
        word = ent.get("word", "").strip()
        key = (ent.get("entity_group"), word.lower())
        if word and key not in seen:
            seen.add(key)
            # cast floats to Python floats
            cleaned = {k: (float(v) if isinstance(v, (np.float32, np.float64)) else v) for k, v in ent.items()}
            entities.append(cleaned)

    # --- ensure everything is JSON-safe
    response = {
        "prediction": pred,
        "summary": summary,
        "entities": entities,
    }

    return response

@app.get("/fetch_sample")
def fetch_sample():
    feeds = {
        "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
        "Reuters": "http://feeds.reuters.com/reuters/topNews",
        "TechCrunch": "https://techcrunch.com/feed/",
    }

    articles = []
    for source, url in feeds.items():
        d = feedparser.parse(url)
        for entry in d.entries[:3]:  # limit to 3 per source
            articles.append({
                "source": source,
                "title": entry.title,
                "summary": getattr(entry, "summary", "")[:300],
                "text": getattr(entry, "description", "")[:1000],
                "link": entry.link
            })
    return articles


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)