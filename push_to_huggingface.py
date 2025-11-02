from huggingface_hub import HfApi, upload_folder
import os

# 🪪 1️⃣ Make sure you have logged in already:
# Run this once before:  huggingface-cli login
# Or programmatically:
# from huggingface_hub import login
# login(token="your_hf_token_here")

# 🧠 2️⃣ Define your model repo and folder path
username = "upasanapandey"   # 🔁 replace with your HF username
model_name = "news-classifier"
local_model_path = "models/classifier"

repo_id = f"{username}/{model_name}"

# 🪄 3️⃣ Create the repo on Hugging Face Hub if it doesn't exist
api = HfApi()

try:
    api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)
    print(f"✅ Repo created or already exists: https://huggingface.co/{repo_id}")
except Exception as e:
    print("⚠️ Could not create repo:", e)

# 🚀 4️⃣ Upload your local model folder
upload_folder(
    folder_path=local_model_path,
    path_in_repo="",          # upload everything to repo root
    repo_id=repo_id,
    repo_type="model"
)

print(f"🎉 Model successfully uploaded to https://huggingface.co/{repo_id}")
