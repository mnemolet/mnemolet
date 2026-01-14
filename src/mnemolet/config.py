import os
import textwrap
import tomllib
from pathlib import Path

prompt = textwrap.dedent("""
# Role
You are a helpful and professional assistant. Your goal is to provide accurate
answers based on the information provided.

---

### Instructions:
1. **Context Priority:** If "Reference Context" contains information,
prioritize it. Use citations (e.g., "According to Document 1...") when possible.
2. **Missing Information:** If the Context is present but lacks the answer,
state that the documents don't contain the specific details before providing
a general answer.
3. **General Knowledge:** If the Context is empty or contains
"[No context provided]", answer the question directly and naturally using your
internal knowledge.
4. **Tone:** Maintain a natural conversation. Do NOT explain your internal
reasoning or state "I am answering based on my knowledge" unless the user asks
where the info came from.
""")

DEFAULT_CONFIG = {
    "qdrant": {
        "host": "localhost",
        "port": 6333,
        "collection": "documents",
        "top_k": 5,
        "min_score": 0.35,
    },
    "ingestion": {
        "batch_size": 100,
        "chunk_size": 1048576,
        "size_chars": 3000,
    },
    "embedding": {
        "model": "all-MiniLM-L6-v2",
        "batch_size": 100,
    },
    "ollama": {"host": "localhost", "port": 11434, "model": "llama3", "prompt": prompt},
    "storage": {
        "db_path": "./data/tracker.sqlite",
        "upload_dir": "./data/uploads",
    },
}

CONFIG_PATH = Path(
    os.getenv("CONFIG_PATH", Path(__file__).resolve().parents[2] / "config.toml")
)


def ensure_file(path: Path, content_bytes: bytes):
    """Ensure a file exists. If not, create it with the provided content."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(content_bytes)


def load_config(path: Path = CONFIG_PATH):
    """
    Load configuration from TOML file.
    """
    import tomli_w

    # Automatically init if missing
    ensure_file(CONFIG_PATH, tomli_w.dumps(DEFAULT_CONFIG).encode())

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
