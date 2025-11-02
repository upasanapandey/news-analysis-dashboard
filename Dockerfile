FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy your trained model into the image
#COPY models/classifier/ ./models/classifier/

COPY src/ ./src/

# Expose port 7860 (Hugging Face expects this)
EXPOSE 7860

# Run the FastAPI server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7860"]