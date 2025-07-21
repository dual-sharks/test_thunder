# TD25 Money Money Money

This project provides a complete Docker-based environment for analyzing financial data using:
- **DuckDB** for fast SQL analytics on CSV data
- **Ollama** with Llama 3.1 for AI-powered insights
- **Flask API** for data queries
- **Jupyter Notebook** for interactive analysis
- **Dify** for LangChain workflows (optional)

## 🏗️ Architecture

### Simple Stack (Recommended)
```
┌─────────────────┐    ┌─────────────────┐
│   Jupyter Lab   │    │  Flask API      │
│   Port: 8888    │    │  Port: 5000     │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┼──────────────┐
                                 │              │
         ┌─────────────────┐    ┌─────────────────┐
         │     Ollama      │    │     DuckDB      │
         │   (Llama 3.1)   │    │  (In-Memory)    │
         │   Port: 11434   │    │   Analytics     │
         └─────────────────┘    └─────────────────┘
                                         │
                                ┌─────────────────┐
                                │   CSV Data      │
                                │  (External Vol) │
                                └─────────────────┘
```

### Full Stack (With Dify)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dify Web UI   │    │   Jupyter Lab   │    │  Flask API      │
│   Port: 3000    │    │   Port: 8888    │    │  Port: 5000     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
         │     Ollama      │    │     DuckDB      │    │      Dify       │
         │   (Llama 3.1)   │    │   (Analytics)   │    │   (LangChain)   │
         │   Port: 11434   │    │    In-Memory    │    │   Port: 5001    │
         └─────────────────┘    └─────────────────┘    └─────────────────┘
                                         │
                                ┌─────────────────┐
                                │   CSV Data      │
                                │  (External Vol) │
                                └─────────────────┘
```

## 📁 Project Structure

```
td25-money/
├── data/
│   └── sample_data.csv          # Financial transaction data
├── duckdb_service/
│   ├── app.py                   # Flask API for data queries
│   └── financial_analysis.ipynb # Jupyter notebook for analysis
├── docker-compose.yml           # Simple stack (default/recommended)
├── docker-compose-full.yml     # Full stack with Dify
├── Dockerfile.duckdb           # DuckDB service container
├── requirements.txt            # Python dependencies
├── setup.sh                    # Automated setup script
├── start.sh                    # Service startup script
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- At least 4GB RAM available for containers
- 5GB free disk space

### ⚡ **Quick Setup (5 minutes)**

1. **Start the Simple Stack:**
   ```bash
   cd td25-money
   docker-compose up -d
   ```

2. **Download AI Model (in background):**
   ```bash
   docker exec ollama ollama pull llama3.1
   ```

3. **Test the Setup:**
   ```bash
   # Test API health
   curl http://localhost:5000/health
   
   # Get financial summary
   curl http://localhost:5000/summary
   
   # Open Jupyter Notebook
   # Visit: http://localhost:8888
   ```

4. **Try AI Analysis:**
   ```bash
   curl -X POST http://localhost:5000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is my biggest expense category?"}'
   ```

✅ **You're now ready to analyze your financial data with AI!**

---

### 1. Start the Stack

**Option A: Simple Stack (Default - Recommended)**
```bash
# Clone or navigate to the project directory
cd td25-money

# Start the simplified stack with just Ollama and DuckDB
docker-compose up -d

# Check service status
docker-compose ps

# View logs if there are issues
docker-compose logs -f
```

**Option B: Full Stack with Dify (Advanced)**
```bash
# Start the full stack with Dify
docker-compose -f docker-compose-full.yml up -d

# Check service status
docker-compose -f docker-compose-full.yml ps

# View logs if there are issues
docker-compose -f docker-compose-full.yml logs -f
```

### 2. Download AI Model

Once Ollama is running, download the Llama 3.1 model:

```bash
# Download the AI model (this may take several minutes)
docker exec ollama ollama pull llama3.1
```

### 3. Access the Services

**Simple Stack Services:**
| Service | URL | Purpose |
|---------|-----|---------|
| **Jupyter Notebook** | http://localhost:8888 | Interactive data analysis |
| **Flask API** | http://localhost:5000 | REST API for data queries |
| **Ollama API** | http://localhost:11434 | AI model inference |

**Full Stack Services (if using docker-compose.yml):**
| Service | URL | Purpose |
|---------|-----|---------|
| **Jupyter Notebook** | http://localhost:8888 | Interactive data analysis |
| **Flask API** | http://localhost:5000 | REST API for data queries |
| **Dify Web UI** | http://localhost:3000 | AI workflow interface |
| **Ollama API** | http://localhost:11434 | AI model inference |

## 📊 Sample Data

> **🎉 COMPLETE SUCCESS!**
> 
> ✅ **Simple Stack:** `docker-compose up -d` (default - recommended for simplicity)
> - DuckDB service: ✅ Running with in-memory database  
> - Ollama AI: ✅ Ready for AI model with Llama 3.1
> - Jupyter Notebook: ✅ Available at http://localhost:8888
> - Flask API: ✅ All endpoints functional at http://localhost:5000
> 
> ✅ **Full Stack:** `docker-compose -f docker-compose-full.yml up -d` (advanced - all features working!)
> - All simple stack features: ✅ Working
> - Dify Web UI: ✅ Available at http://localhost:3000
> - Dify API: ✅ Available at http://localhost:5001
> - Database: ✅ PostgreSQL, Redis, Weaviate all connected
> - LangChain workflows: ✅ Ready for advanced AI workflows

The `data/sample_data.csv` contains financial transaction data with the following structure:

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | INTEGER | Unique identifier |
| date | DATE | Transaction date |
| amount | DECIMAL | Amount (positive=income, negative=expense) |
| category | VARCHAR | Transaction category |
| description | VARCHAR | Transaction description |
| merchant | VARCHAR | Merchant name |
| account_type | VARCHAR | Account type (checking, credit) |

## 🔧 API Endpoints

### DuckDB Service (Port 5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/summary` | GET | Financial data summary |
| `/categories` | GET | Spending by category |
| `/query` | POST | Execute SQL query |
| `/ask` | POST | Natural language query |

### Example API Usage

```bash
# Get financial summary
curl http://localhost:5000/summary

# Ask a natural language question
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is my total spending on food this month?"}'

# Execute SQL query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT category, SUM(ABS(amount)) as total FROM transactions WHERE amount < 0 GROUP BY category ORDER BY total DESC"}'
```

## 🧠 AI-Powered Analysis

### Natural Language Queries

The system can answer questions like:
- "What's my biggest expense category?"
- "How much did I spend on food last month?"
- "Show me all transactions over $100"
- "What's my average monthly income?"

### Available AI Model

- **Llama 3.1** (8B parameters): Excellent for financial analysis, SQL generation, and data insights

## 🔄 Using Dify for LangChain Workflows

1. Access Dify at http://localhost:3000
2. Create a new workflow
3. Connect to the DuckDB API at `http://duckdb-service:5000`
4. Use Ollama at `http://ollama:11434` for AI processing

## 📓 Jupyter Analysis

The included notebook provides:
- Data loading from the external volume
- Basic financial analysis
- DuckDB integration examples
- Visualization templates

## 🛠️ Development

### Adding New Data

```bash
# Add new CSV files to the data directory
cp new_transactions.csv data/

# Restart DuckDB service to reload data
docker-compose restart duckdb-service
```

### Customizing the AI Model

```bash
# Try different Ollama models
docker exec ollama ollama pull codellama
docker exec ollama ollama pull mistral
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://ollama:11434` | Ollama service URL |
| `DATABASE_URL` | `postgresql://...` | Dify database connection |
| `REDIS_URL` | `redis://redis:6379` | Redis connection for Dify |

## 🔍 Troubleshooting

### Common Issues

1. **DuckDB File Lock Error**: 
   ```bash
   # This is already fixed in the current version using in-memory database
   # If you encounter this, make sure you're using the latest code
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Dify Worker Database Connection Error** (Full Stack Only): 
   ```bash
   # Stop all services and restart with proper dependencies
   docker-compose down
   docker-compose up -d postgres redis
   # Wait 30 seconds for databases to be ready
   sleep 30
   docker-compose up -d
   ```

3. **Dify Plugin Daemon Warnings** (Full Stack Only): 
   ```bash
   # These error messages are harmless and can be ignored:
   # "PluginDaemonInnerError: Request to Plugin Daemon Service failed"
   # The plugin system is optional and doesn't affect core functionality
   # All services remain fully functional despite these warnings
   ```

4. **Out of Memory**: Increase Docker memory allocation to 8GB+

5. **Model Download Fails**: Check internet connection and disk space

6. **Port Conflicts**: Ensure ports 5000, 8888, 11434 are available (and 3000 for full stack)

7. **Services Not Starting**:
   ```bash
   # For simple stack (default)
   docker-compose down -v
   docker-compose up -d
   
   # For full stack
   docker-compose -f docker-compose-full.yml down -v
   docker volume prune -f
   docker-compose -f docker-compose-full.yml up -d
   ```

### Useful Commands

```bash
# Simple Stack Commands (Default)
docker-compose ps        # Check service status
docker-compose logs      # View all logs
docker-compose logs duckdb-service  # View specific service logs
docker-compose restart duckdb-service  # Restart specific service
docker-compose down      # Stop all services

# Full Stack Commands (if using Dify)
docker-compose -f docker-compose-full.yml ps                                      # Check service status
docker-compose -f docker-compose-full.yml logs [service-name]                     # View service logs
docker-compose -f docker-compose-full.yml restart [service-name]                  # Restart specific service
docker-compose down -v                                 # Clean up

# Test the API
curl http://localhost:5000/health                      # Health check
curl http://localhost:5000/summary                     # Get financial summary
```

## 📈 Performance Tips

1. **DuckDB**: Automatically optimized for analytical queries
2. **Memory**: Increase Docker memory for better performance
3. **Storage**: Use SSD storage for faster data access
4. **AI Model**: Llama 3.1 provides good balance of speed and accuracy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new analysis capabilities
4. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

---

**Happy Analyzing! 🎉**

For questions or support, please open an issue in the repository.
