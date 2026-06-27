# 🚀 AtlasML

> **Autonomous Machine Learning Research Scientist**

AtlasML is an AI-powered AutoML platform that automates the machine learning workflow—from dataset understanding to model training, evaluation, explainability, and intelligent reporting.

The vision behind AtlasML is to build an AI system that behaves like a Machine Learning Engineer by understanding datasets, recommending preprocessing steps, selecting appropriate models, training them automatically, and explaining the results in a user-friendly way.

---

## 📌 Current Status

**Version:** Sprint 2 (Foundation & Dataset Profiling)

AtlasML currently supports intelligent CSV dataset ingestion and profiling through a FastAPI backend.

---

# ✨ Features

### ✅ Dataset Upload

* Upload CSV datasets through REST API
* File validation
* Exception handling

### ✅ Dataset Profiling

* Dataset dimensions
* Column names
* Data types
* Missing value analysis
* Dataset preview
* Duplicate row detection
* Memory usage analysis
* Missing value percentage

### ✅ Feature Analysis

Automatically identifies:

* Numerical Features
* Categorical Features
* Boolean-like Features

---

# 🏗️ Project Architecture

```
AtlasML
│
├── backend
│   ├── agents
│   ├── api
│   ├── models
│   ├── pipelines
│   ├── services
│   ├── tests
│   ├── utils
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
│
├── frontend
├── datasets
├── docs
├── experiments
├── reports
│
├── README.md
├── CHANGELOG.md
└── .gitignore
```

---

# ⚙️ Tech Stack

### Backend

* Python
* FastAPI
* Pandas
* Uvicorn

### Version Control

* Git
* GitHub

---

# 📡 API Endpoints

## Health Check

```
GET /health
```

Returns server status.

---

## Upload Dataset

```
POST /upload
```

Uploads a CSV dataset and returns:

* Dataset dimensions
* Column names
* Data types
* Feature summary
* Missing values
* Dataset quality metrics
* Dataset preview

---

# 🚀 Getting Started

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AtlasML.git
```

Navigate into the project

```bash
cd AtlasML
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

### Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r backend/requirements.txt
```

Run the application

```bash
uvicorn backend.main:app --reload
```

Open Swagger UI

```
http://127.0.0.1:8000/docs
```

---

# 📈 Current Development Progress

## ✅ Completed

* Project architecture
* FastAPI backend
* Modular routing
* Service layer
* CSV upload
* Dataset profiling
* Feature summary
* Dataset quality metrics
* Swagger API documentation
* Error handling

---

# 🛣️ Roadmap

## Sprint 3

* Intelligent dataset analysis
* Target column detection
* Classification vs Regression detection
* Identifier column detection
* Constant feature detection

## Sprint 4

* Automated data cleaning
* Missing value treatment
* Duplicate removal
* Encoding
* Scaling

## Sprint 5

* Automated model training
* Model comparison
* Performance metrics

## Sprint 6

* Explainable AI (SHAP)
* Feature importance
* Model explanations

## Sprint 7

* AI Agents
* Workflow orchestration
* LLM integration

## Sprint 8+

* Frontend
* Authentication
* Deployment
* MLOps integration

---

# 🎯 Long-Term Vision

AtlasML aims to become a fully autonomous Machine Learning Research Assistant capable of:

* Understanding datasets
* Performing intelligent preprocessing
* Selecting appropriate ML algorithms
* Training and evaluating models
* Explaining predictions
* Generating comprehensive reports
* Assisting users throughout the complete machine learning lifecycle

---

# 📄 License

This project is currently under active development for educational and research purposes.
