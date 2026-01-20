# mimicryML - AI Style Transfer Studio

Transform your photos into artistic masterpieces using deep learning.

## Features
- Neural style transfer with multiple artistic styles
- FastAPI backend for ML processing
- Streamlit frontend for user interface
- SQLite database for transformation history

## Setup

1. Clone the repository
2. Create virtual environment:
```bash
   python3 -m venv venv
   source venv/bin/activate
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```

## Running the Application

### Backend (FastAPI)
```bash
cd backend
uvicorn main:app --reload
```
Visit: http://localhost:8000

### Frontend (Streamlit)
```bash
cd frontend
streamlit run app.py
```
Visit: http://localhost:8501

## Project Structure
```
ai-style-transfer/
├── backend/          # FastAPI application
├── frontend/         # Streamlit UI
├── models/           # Pre-trained models
├── uploads/          # User uploaded images
├── outputs/          # Stylized results
└── database/         # SQLite database
```

## Technologies
- Python 3.9+
- FastAPI
- Streamlit
- TensorFlow/PyTorch
- SQLite
