from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import uvicorn
import feedparser

app = FastAPI()
MODEL_PATH = "models/classifier"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# Pipelines
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
ner = pipeline("ner", grouped_entities=True)  # uses default model

labels = ["World", "Sports", "Business", "Sci/Tech"]  # AG News mapping

class Query(BaseModel):
    text: str


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
    pred = predict(q)  # reuse logic
    summary = summarizer(q.text, max_length=60, min_length=20, do_sample=False)[0]['summary_text']
    entities = ner(q.text)

    # Convert entity scores to float
    for e in entities:
        if "score" in e:
            e["score"] = float(e["score"])

    return {
        "prediction": pred,
        "summary": summary,
        "entities": entities
    }
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
