"""
OTHERS ARCHITECTURAL RULES (v0.2.0)
Focus: Enterprise Nested Structure for Specialized Systems.
Pattern: Nested Source (src) and Internal Logic separation.
"""

OTHERS_RULES = {
    "base": {
        "packages": [
            "src",
            "src/core",
            "src/services",
            "src/utils",
            "tests"
        ],
        "folders": [
            "docs",
            "logs",
            "scripts"
        ]
    },
    "rag_ai": {
        "packages": [
            "src",
            "src/api",              # Entry interfaces (FastAPI/LiteLLM)
            "src/core",             # LLM settings & Auth
            "src/engine",           # Root AI Logic
            "src/engine/chains",    # Execution flows (LangGraph/Chain)
            "src/engine/retrievers",# Retrieval algorithms
            "src/engine/embedders", # Vectorization
            "src/storage",          # DB & Vector Store drivers (Chroma/Qdrant)
            "src/prompts",          # Prompt templates (.yaml/.txt)
            "tests",
            "tests/integration",
            "tests/unit"
        ],
        "folders": [
            "data",
            "data/raw",             # Source documents
            "data/vector_store",    # Local index storage
            "docs", 
            "logs", 
            "notebooks"             # For AI experimentation/EDA
        ]
    },
    "mlops_core": {
        "packages": [
            "src",
            "src/training",         # Model training code
            "src/inference",        # Model serving logic
            "src/preprocessing",    # Feature engineering
            "src/registry",         # Tracking logic (MLFlow/Bentoml)
            "src/core",             # Hyperparams & Optuna logic
            "internal",             # Private utilities
            "tests"
        ],
        "folders": [
            "artifacts",            # Weights and models (.pth, .onnx, .bin)
            "data/validation",
            "data/train",
            "notebooks",
            "logs"
        ]
    },
    "data_pipeline": {
        "packages": [
            "src",
            "src/dags",             # Workflow orchestration (Prefect/Dagster)
            "src/operators",        # Custom ETL tools
            "src/transformers",     # Data cleaning logic
            "src/connectors",       # S3/SQL/API connectors
            "src/schemas",          # Validation logic (Pydantic/GreatExpectations)
            "tests"
        ],
        "folders": [
            "staging",              # Intermediate file storage (Parquet/Avro)
            "sql",                  # Pure SQL scripts
            "assets",               # Meta-definitions
            "logs"
        ]
    },
    "dbt_analytics": {
        "packages": [
            "analytics",
            "analytics/macros",
            "tests"
        ],
        "folders": [
            "models",
            "models/staging",
            "models/marts",
            "seeds",
            "snapshots",
            "analyses",
            "docs",
            "logs"
        ]
    },
    "hp_cli": {
        "packages": [
            "src",
            "src/commands",         # Sub-command logic (Typer/Click)
            "src/core",             # Main entry setup
            "src/ui",               # Rich/Terminal formatting logic
            "internal",             # Backend system calls
            "tests"
        ],
        "folders": [
            "docs/man",             # Manual pages
            "scripts/completions"   # Shell completion scripts (Zsh/Bash)
        ]
    }
}
