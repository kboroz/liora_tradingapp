# Liora Trading App 

A production-grade cryptocurrency trading system with machine learning predictions, real-time data ingestion, and comprehensive monitoring.

## What's Included

- **Data Ingestion**: Real-time Binance API integration
- **Feature Engineering**: 6+ technical indicators
- **ML Models**: LightGBM + LSTM neural networks
- **FastAPI**: REST API with full documentation
- **Database**: PostgreSQL with async support
- **Caching**: Redis for performance
- **Monitoring**: Prometheus + Grafana dashboards
- **Testing**: Comprehensive test suite
- **Docker**: Full containerization

### Quick Start

#### 1. Clone Repository

```bash
git clone https://github.com/kboroz/liora_tradingapp.git
cd liora_tradingapp

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your Binance API keys

docker-compose up -d

curl http://localhost:8000/api/v1/health

curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "features": {"volatility_20": 0.02}}'

liora_tradingapp/
├── src/
│   ├── api/              # FastAPI application
│   ├── models/           # ML models (LightGBM, LSTM, XGBoost)
│   ├── features/         # Feature engineering
│   ├── database/         # DB & Redis utilities
│   ├── monitoring/       # Prometheus metrics
│   ├── ingestion/        # Binance data ingestion
│   └── utils/            # Helper utilities
├── tests/                # Pytest suite
├── models/               # Trained models
├── data/                 # Data storage
├── config/               # Config files & Grafana/Prometheus
├── reports/              # EDA reports
├── docker-compose.yml    # Service orchestration
├── Dockerfile            # API container
└── README.md             # This file

pytest tests/ -v

python -m uvicorn src.api.main:app --reload

# Build production image
docker build -t liora-api:latest .

# Push to registry
docker push your-registry/liora-api:latest

# Deploy with Docker Compose or Kubernetes
docker-compose -f docker-compose.prod.yml up


## Step 9: Update requirements.txt

```bash
cd ~/liora_tradingapp && cat > requirements.txt << 'EOF'
# Core
pandas==2.0.3
numpy==1.24.3
python-dotenv==1.0.0

# API
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.4.2

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1

# ML Models
scikit-learn==1.3.2
xgboost==2.0.2
lightgbm==4.0.0
tensorflow==2.14.0

# Data Collection
python-binance==1.0.17
aiohttp==3.9.1

# Monitoring
prometheus-client==0.18.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Development
black==23.12.0
flake8==6.1.0
mypy==1.7.1
