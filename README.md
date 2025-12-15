# mnemolet-core

**MnemoLet** is a minimal, end-to-end **Retrieval-Augmented Generation (RAG)**
system that runs entirely **locally**: no API keys, no cloud.

## MVP Goals

### Core objectives

- Ingest plain `.txt` files
- Chunk text with configurable overlap
- Embed chunks using a local sentence-transformer model
- Store embeddings in a local Qdrant vector database
- Track ingested files and hashes in a local SQLite database
- Retrieve top-k most relevant chunks for a query
- Generate answers using a local LLM (via [Ollama](https://ollama.ai) or compatible API)
- Provide a clean command-line interface (`ingest`, `query`)

## Run Qdrant

Before running the container, create a storage directory:

`$ mkdir -p ./qdrant_storage`

with docker:

```
docker run -p 6333:6333 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

with podman:

```
podman run -p 6333:6333 \
    -v ./qdrant_storage:/qdrant/storage \
    docker.io/qdrant/qdrant
```

## Installation

MnemoLet requires Python and [uv](https://uv.run/) for managing virtual environments and dependencies.

1. **clone the repo**:

`git clone https://github.com/mnemolet/mnemolet-core.git`

2. **install dependencies**

`uv sync`

3. install the project in editable mode

`uv pip install -e .`

3. **verify installation**

`mnemolet --version`

`mnemolet --help`

## Configuration

MnemoLet uses a `config.toml` file to configure Qdrant, 
embeddings, Ollama, and local storage.

Below is default configuration:

```
[qdrant]
host = "localhost"
port = 6333
collection = "documents"
top_k = 5
min_score = 0.35

[ingestion]
batch_size = 100
chunk_size = 1048576 # 1Mb
size_chars = 3000

[embedding]
model = "all-MiniLM-L6-v2"
batch_size = 100

[ollama]
host = "localhost"
port = 11434
model = "llama3"

[storage]
db_path = "./data/tracker.sqlite"
upload_dir = "./data/uploads"
```

## CLI

**Note:** Before using the CLI or API, make sure the Qdrant server is running.

### Version

`mnemolet --version`

or

`uv run python -m mnemolet.cli.main --version`

### Help

`mnemolet --help`

or

`uv run python -m mnemolet.cli.main --help`

### Dashboard: Show system and service health status.

`mnemolet dashboard`

### Init-config: Generate a default config.toml file.

`mnemolet init-config`

### List-collections: List all Qdrant collections.

`mnemolet list-collections`

### Remove: Remove Qdrant collection.

`mnemolet remove <collection_name> STR`

### Ingest Files

`mnemolet ingest <directory>`

or

`uv run python -m mnemolet.cli.main ingest <directory>`

or

add `--force` to re-ingest files and recreate Qdrant collection

`uv run python -m mnemolet.cli.main ingest <directory> --force`

`-v` - optional verbosity flag (can be repeated as -vv for debug mode)

#### Example:

`mnemolet -v ingest /path/to/docs`

### Search in Qdrant Collection

`mnemolet search "<query>"`

or

`uv run python -m mnemolet.cli.main search "<query>"`

- `--top-k <INT>` - optional number of results to retrieve

- `--min-score <FLOAT>` - optional minimum score threshold [default: 0.35]

#### Example:

`mnemolet search "example" --top-k 5 --min-score 0.2`

### Generate Answer

`mnemolet answer "<query>"`

or

`uv run python -m mnemolet.cli.main answer "<query>"`

- `--top-k <INT>` - optional number of results to retrieve

- `--min-score <FLOAT>` - optional minimum score threshold [default: 0.35]

- `--ollama-url <STR>` - optional Ollama url [default: http://localhost:11434]

- `--ollama-model <STR>` - optional local model to use for generation [default: llama3]

#### Example:

`mnemolet answer "example" --top-k 5 --min-score 0.2`

## API

The API is implemented using [FastAPI](https://fastapi.tiangolo.com/).

### Available Endpoint

- **`GET /search`**: Search indexed texts.

**Query Parameters:**
- `query` (str) - search query.
- `top_k` (int, optional) - number of results to return (default: 3).

- **`GET /answer`**: Search indexed texts.

**Query Parameters:**
- `query` (str) - search query.
- `top_k` (int, optional) - number of results to return (default: 3).

### Running the API

Start the FastAPI server with:

`uv run uvicorn api.server:app --reload`

### Testing the Endpoint

#### Search

`curl "http://127.0.0.1:8000/search?query=<query>"`

or 

`curl "http://127.0.0.1:8000/search?query=<query>&top_k=2"`

#### Answer

`curl "http://127.0.0.1:8000/answer?query=<query>"`

or 

`curl "http://127.0.0.1:8000/answer?query=<query>&top_k=2"`

#### List sessions

`curl "http://127.0.0.1:8000/api/chat/sessions"`

#### Delete session

`curl -i -X DELETE "http://127.0.0.1:8000/api/chat/sessions/<session_id>"`

#### Delete all sessions

`curl -i -X DELETE "http://127.0.0.1:8000/api/chat/sessions?confirm=true"`
