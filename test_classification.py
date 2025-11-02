from transformers import pipeline

clf = pipeline(
    "text-classification",
    model="models/classifier",
    tokenizer="models/classifier"
)

label_names = ["World", "Sports", "Business", "Sci/Tech"]

result = clf("India is launching a space shuttle")[0]
label_id = int(result["label"].split("_")[-1])
print({"label": label_names[label_id], "score": result["score"]})