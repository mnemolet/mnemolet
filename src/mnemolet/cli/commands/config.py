import shutil
import textwrap
from datetime import datetime
from pathlib import Path

import click

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


@click.command("init-config")
@click.option("--path", default="config.toml", help="Path to save config file.")
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite existing config.toml (creates a backup first).",
)
def init_config(path: str, force: bool):
    """
    Generate a default config.toml file.
    """
    import tomli_w

    config_path = Path(path)

    if config_path.exists() and not force:
        click.echo("config.toml already exists. Use --force to overwrite it.")
        return

    if config_path.exists() and force:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        backup_path = config_path.with_suffix(f".toml.bak-{timestamp}")
        click.echo(backup_path)
        shutil.copy2(config_path, backup_path)
        click.echo(f"Existing config backed up as {backup_path.name}")

    with open(config_path, "wb") as f:
        tomli_w.dump(DEFAULT_CONFIG, f)

    click.echo(f"Configuration written to {config_path}.")
