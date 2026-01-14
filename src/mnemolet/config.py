import os
import tomllib
from pathlib import Path

CONFIG_PATH = Path(
    os.getenv("CONFIG_PATH", Path(__file__).resolve().parents[2] / "config.toml")
)


def load_config(path: Path = CONFIG_PATH):
    """
    Load configuration from TOML file.
    """
    with open(path, "rb") as f:
        return tomllib.load(f)


config = load_config()

QDRANT_HOST = os.getenv("QDRANT_HOST", config["qdrant"]["host"])
QDRANT_PORT = int(os.getenv("QDRANT_PORT", config["qdrant"].get("port", 6333)))
QDRANT_COLLECTION = config["qdrant"]["collection"]
QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"
TOP_K = int(os.getenv("TOP_K", config["qdrant"].get("top_k", 5)))
MIN_SCORE = float(os.getenv("MIN_SCORE", config["qdrant"].get("min_score", 0.35)))

BATCH_SIZE = int(os.getenv("BATCH_SIZE", config["ingestion"].get("batch_size", 100)))
# 1 MB == 1024 * 1024
CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", config["ingestion"].get("chunk_size", 1048576))
)
SIZE_CHARS = int(os.getenv("SIZE_CHARS", config["ingestion"].get("size_chars", 3000)))

EMBED_MODEL = os.getenv("EMBED_MODEL", config["embedding"]["model"])
EMBED_BATCH = int(os.getenv("EMBED_BATCH", config["embedding"].get("batch_size", 100)))

OLLAMA_HOST = os.getenv("OLLAMA_HOST", config["ollama"]["host"])
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", config["ollama"].get("port", 11434)))
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", config["ollama"]["model"])
OLLAMA_PROMPT = os.getenv("OLLAMA_PROMPT", config["ollama"]["prompt"])

DB_PATH = Path(os.path.expanduser(config["storage"]["db_path"]))

UPLOAD_DIR = Path(config["storage"]["upload_dir"])
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
