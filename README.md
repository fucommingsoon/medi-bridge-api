# Medi-Bridge API

Medical Consultation Assistant API Service - Intelligent Symptom Retrieval System Based on Vector Database

## Project Overview

Medi-Bridge API is a backend service for medical consultation assistants. The system receives symptom descriptions from users, searches for matching medical information through vector retrieval technology in Qdrant vector database, and returns relevant medical knowledge references.

### Core Features

- **Symptom Retrieval**: Accept user symptom descriptions and return relevant medical information
- **Vector Search**: Efficient similarity retrieval based on Qdrant vector database
- **RESTful API**: Standardized REST API interface design

## Tech Stack

| Technology | Version | Description |
|------------|---------|-------------|
| Python | 3.11+ | Runtime environment |
| FastAPI | 0.115.0 | Web framework |
| Qdrant | 1.12.1 | Vector database |
| Pydantic | 2.10.3 | Data validation |
| Uvicorn | 0.32.0 | ASGI server |

## Project Structure

```
medi-bridge-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── consultation.py    # Consultation API
│   │       └── router.py          # Router aggregation
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   └── exceptions.py          # Custom exceptions
│   ├── models/
│   │   └── vector_db.py           # Qdrant client wrapper
│   ├── schemas/
│   │   ├── consultation.py        # Consultation data models
│   │   └── health.py              # Health check models
│   ├── services/
│   │   └── vector_search.py       # Vector search service
│   └── main.py                    # Application entry point
├── tests/                          # Test directory
├── .env.example                    # Environment variables example
├── .gitignore
├── requirements.txt                # Dependencies list
└── README.md
```

## Quick Start

### Requirements

- Python 3.11 or higher
- Qdrant vector database (local or cloud)

### Installation

1. **Clone repository**
```bash
git clone https://github.com/fucommingsoon/medi-bridge-api.git
cd medi-bridge-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env file with actual configuration
```

5. **Start Qdrant**
```bash
# Start local Qdrant using Docker
docker run -p 6333:6333 qdrant/qdrant
```

6. **Run service**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Documentation

After starting the service, visit the following URLs to view API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
```
GET /
```

### Symptom Query
```
POST /api/v1/consultation/query
Content-Type: application/json

{
  "query": "headache and fever",
  "top_k": 5
}
```

### Vector Database Health Check
```
GET /api/v1/consultation/health
```

## Configuration

| Environment Variable | Default | Description |
|----------------------|---------|-------------|
| `QDRANT_HOST` | localhost | Qdrant server address |
| `QDRANT_PORT` | 6333 | Qdrant port |
| `QDRANT_COLLECTION_NAME` | medical_knowledge | Collection name |
| `QDRANT_API_KEY` | - | Qdrant API key (optional) |
| `VECTOR_SIZE` | 768 | Vector dimension |
| `TOP_K_RESULTS` | 5 | Default number of results to return |
| `SIMILARITY_THRESHOLD` | 0.7 | Similarity threshold |

## Development

### Code formatting
```bash
black app/
ruff check app/
```

### Run tests
```bash
pytest
```

## Important Medical Disclaimer

> **Warning**: The AI consultation advice provided by this software is for reference only and does not constitute medical diagnosis, treatment advice, or professional medical opinion.

- Users should always consult licensed doctors for medical advice
- Developers are not liable for any health damage, misdiagnosis, or treatment delays caused by using this software
- This software has not been certified by any national drug administration or medical device regulatory authority

## License

This project is licensed under [LICENSE](LICENSE).

## Contact

- GitHub: [fucommingsoon](https://github.com/fucommingsoon)
