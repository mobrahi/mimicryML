# 🎨 AI Style Transfer Studio

Transform your photos into artistic masterpieces using deep learning and neural style transfer. A full-stack machine learning application built as a Python bootcamp final project.

![Project Status](https://img.shields.io/badge/status-completed-success)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 📸 Demo

> Add screenshots here after completing the project

### What It Does
Upload any photo and transform it into the style of famous artists like Van Gogh, Picasso, Monet, or Kandinsky using neural style transfer powered by deep learning.

---

## ✨ Features

- 🎨 **4 Artistic Styles**: Van Gogh (Starry Night), Picasso (Cubism), Monet (Impressionism), Kandinsky (Abstract)
- 🚀 **Async Processing**: Background job processing with real-time status updates
- 📊 **Job Tracking**: Monitor transformation progress with detailed status
- 📜 **History**: View all your past transformations with statistics
- 🖼️ **Gallery**: Browse transformations from all users
- 💾 **Download Results**: Save your artistic masterpieces
- 📱 **Responsive UI**: Beautiful, modern interface with gradient design
- 🔄 **RESTful API**: Well-documented API with Swagger UI

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **TensorFlow** - Deep learning framework for style transfer
- **TensorFlow Hub** - Pre-trained arbitrary image stylization model
- **SQLite** - Lightweight database for job tracking
- **aiosqlite** - Async database operations
- **Pillow** - Image processing

### Frontend
- **Streamlit** - Interactive web application framework
- **Requests** - HTTP library for API communication

### Machine Learning
- **Model**: Arbitrary Image Stylization v1-256 (Magenta)
- **Approach**: Transfer learning with pre-trained CNN
- **Technique**: Neural style transfer using Gram matrices

---
## Architecture Diagram
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │
       ↓
┌─────────────────┐
│   Streamlit     │  ← Frontend UI
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/REST API
         ↓
┌─────────────────┐
│    FastAPI      │  ← Backend Server
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┐
    ↓          ↓          ↓
┌────────┐ ┌──────┐ ┌─────────────┐
│ SQLite │ │ Files│ │ TensorFlow  │
│   DB   │ │System│ │  (ML Model) │
└────────┘ └──────┘ └─────────────┘

---
## 📁 Project Structure
```
mimicryML | ai-style-transfer/
├── backend/
│   ├── main.py              # FastAPI application & endpoints
│   ├── style_transfer.py    # Neural style transfer logic
│   ├── database.py          # SQLite database operations
│   ├── config.py            # Configuration & constants
│   ├── templates/           # HTML templates
│   │   └── index.html       # Landing page
│   └── utils/
│       ├── download_styles.py
│       └── create_sample_styles.py
├── frontend/
│   └── app.py               # Streamlit web interface
├── models/
│   └── style_images/        # Reference style images for transfer
│       ├── vangogh.jpg      # Van Gogh - Starry Night style
│       ├── picasso.jpg      # Picasso - Cubism style
│       ├── monet.jpg        # Monet - Impressionism style
│       └── kandinsky.jpg    # Kandinsky - Abstract style
├── uploads/                 # User uploaded images (temporary)
├── outputs/                 # Stylized output images
├── database/
│   └── style_transfer.db    # SQLite database
├── requirements.txt
└── README.md
```

**Note:** The pre-trained TensorFlow model is automatically downloaded 
and cached by TensorFlow Hub in `ls -lh $TMPDIR/tfhub_modules` on first use.
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/ai-style-transfer.git
cd ai-style-transfer
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Download Style Images
```bash
# Option 1: Automated download
python3 backend/utils/download_styles.py

# Option 2: Create sample styles
python3 backend/utils/create_sample_styles.py
```

### Step 5: Initialize Database
The database is automatically created when you first run the backend.

---

## 💻 Running the Application

You need to run both backend and frontend simultaneously in separate terminals.

### Terminal 1: Start Backend Server
```bash
cd backend
uvicorn main:app --reload
```
Backend will be available at: `http://127.0.0.1:8000`

- API Docs: http://127.0.0.1:8000/docs
- Landing Page: http://127.0.0.1:8000

### Terminal 2: Start Frontend Application
```bash
cd frontend
streamlit run app.py
```
Frontend will open automatically at: `http://localhost:8501`

---

## 📖 Usage Guide

### Using the Web Interface (Streamlit)

1. **Transform Page**:
   - Upload your photo (JPG, JPEG, or PNG)
   - Select an artistic style
   - Click "Transform My Image"
   - Wait for processing (5-30 seconds)
   - View before/after comparison
   - Download your stylized image

2. **History Page**:
   - View all your transformations
   - See statistics (total, completed, avg time)
   - Access past results

3. **Gallery Page**:
   - Browse transformations from all users
   - Get inspiration from community creations

### Using the API Directly

**1. Upload and Transform**
```bash
curl -X POST "http://127.0.0.1:8000/transform?style=vangogh" \
  -F "file=@/path/to/your/photo.jpg"
```

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "pending",
  "message": "Image uploaded successfully. Processing started."
}
```

**2. Check Status**
```bash
curl http://127.0.0.1:8000/status/abc-123-def-456
```

**3. Download Result**
```bash
curl http://127.0.0.1:8000/result/abc-123-def-456 --output stylized.jpg
```

---

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET | `/docs` | Interactive API documentation |
| GET | `/health` | Health check |
| GET | `/styles` | List available styles |
| POST | `/transform` | Upload image and start transformation |
| GET | `/status/{job_id}` | Check job status |
| GET | `/result/{job_id}` | Download stylized image |
| GET | `/history/{session_id}` | Get transformation history |
| GET | `/gallery` | Browse recent transformations |

---

## 🧠 How It Works

### Neural Style Transfer

This project uses **neural style transfer**, a deep learning technique that applies the artistic style of one image to the content of another.

**Key Concepts:**

1. **Pre-trained CNN (VGG19)**: 
   - Extracts features from images at different layers
   - Early layers capture textures, colors
   - Deep layers capture objects, composition

2. **Content Representation**:
   - High-level features from deep layers
   - Preserves the structure and objects in your photo

3. **Style Representation (Gram Matrices)**:
   - Captures correlations between features
   - Represents artistic patterns, brushstrokes, color palettes
   - Ignores spatial arrangement

4. **Optimization Process**:
   - Start with your photo
   - Iteratively adjust pixels to minimize:
     - Content loss (keep photo structure)
     - Style loss (match artistic patterns)
   - Result: Your photo painted in the artist's style

### Technical Flow
```
User Upload → FastAPI receives image
           → Save to uploads/
           → Create database entry
           → Background task starts
           → Load style image
           → Apply TensorFlow model
           → Generate stylized image
           → Save to outputs/
           → Update database (completed)
           → User downloads result
```

---

## 🔧 Configuration

Edit `backend/config.py` to customize:
```python
# Image processing
MAX_IMAGE_SIZE = 512  # Max dimension (larger = better quality, slower)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Style transfer
CONTENT_WEIGHT = 1.0
STYLE_WEIGHT = 1000.0
NUM_ITERATIONS = 500  # More = better quality, slower
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the process if needed
kill -9 <PID>
```

### Frontend can't connect to backend
- Ensure backend is running on `http://127.0.0.1:8000`
- Check firewall settings
- Verify `API_BASE_URL` in `frontend/app.py`

### Style images not found
```bash
# Re-download or recreate them
python3 backend/utils/create_sample_styles.py
```

### Slow processing
- First run downloads model (~100MB) - be patient
- Reduce `MAX_IMAGE_SIZE` in config.py
- Use smaller input images
- Subsequent runs are much faster (model cached)

### Database errors
```bash
# Reset database
rm database/style_transfer.db
# It will be recreated automatically on next run
```

---

## 🎓 Learning Outcomes

### What I Learned

**Technical Skills:**
- Building RESTful APIs with FastAPI
- Async programming in Python
- Database operations with SQLite
- Machine learning integration with TensorFlow
- Frontend development with Streamlit
- File handling and storage management

**Concepts Mastered:**
- Neural style transfer and CNNs
- Transfer learning
- API design patterns
- Background task processing
- Session management
- Error handling and validation

**Development Practices:**
- Project structure and organization
- Virtual environments
- Git version control
- Documentation
- Debugging and troubleshooting

---

## 🚧 Challenges Faced

### Challenge 1: Downloading Style Images
**Problem**: Wikipedia blocked automated downloads (403 Forbidden)  
**Solution**: Used Art Institute of Chicago API and created fallback sample generator

### Challenge 2: Pydantic Validation Errors
**Problem**: Database `None` values failing Pydantic validation  
**Solution**: Used `Optional[type]` for nullable fields

### Challenge 3: First Run Performance
**Problem**: Initial transformation took 60+ seconds  
**Solution**: Understood that TensorFlow downloads model first time; subsequent runs ~10s

### Challenge 4: Async Database Operations
**Problem**: Blocking database calls in async endpoints  
**Solution**: Implemented aiosqlite for async database operations

### Challenge 5: File Path Management
**Problem**: Relative paths breaking across different run locations  
**Solution**: Used `Path(__file__).resolve().parent` for absolute paths

---

## 🔮 Future Enhancements

**Planned Features:**
- [ ] Style strength slider (blend original with stylized)
- [ ] Multiple style mixing
- [ ] Batch processing (multiple images)
- [ ] User authentication
- [ ] Cloud deployment (AWS/Heroku/Railway)
- [ ] GPU support for faster processing
- [ ] More artistic styles
- [ ] Video style transfer
- [ ] Export transformation as time-lapse
- [ ] Social sharing features

**Technical Improvements:**
- [ ] Redis for job queue
- [ ] PostgreSQL for production database
- [ ] Docker containerization
- [ ] Unit and integration tests
- [ ] CI/CD pipeline
- [ ] Rate limiting
- [ ] Caching layer

---

## 📊 Performance Metrics

- **First transformation**: ~30-60s (model download + processing)
- **Subsequent transformations**: ~5-15s
- **Supported image formats**: JPG, JPEG, PNG
- **Max file size**: 10MB
- **Processing resolution**: 512x512 (configurable)
- **Database**: Lightweight, no size limits

---

## 🤝 Contributing

This is a bootcamp final project, but suggestions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **TensorFlow Team** for the amazing Magenta models
- **FastAPI** for the excellent web framework
- **Streamlit** for making beautiful UIs simple
- **Art Institute of Chicago** for public domain art images
- **Python Bootcamp Instructors** for the guidance
- **Claude (Anthropic)** for technical mentorship throughout development

---

## 📞 Contact

**Fairuz Mohd Ibrahim** - [@faairuz](https://twitter.com/faairuz)

Project Link: [https://github.com/mobrahi/mimicryML]
(https://github.com/yourusername/ai-style-transfer)

---

## 🌟 Star History

If you found this project helpful, please consider giving it a ⭐!

---

**Built with ❤️ and Python | Bootcamp Final Project 2026**