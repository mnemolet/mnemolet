from mnemolet.cuore.utils.qdrant import QdrantManager

from .ollama import get_ollama_status
from .system import get_cpu_stats, get_memory_stats, get_python_version


def get_status(qdrant_url: str, ollama_url: str) -> dict:
    qm = QdrantManager(qdrant_url)

    return {
        "qdrant": qm.check_qdrant_status(),
        "ollama": get_ollama_status(ollama_url),
        "python_version": get_python_version(),
        "memory": get_memory_stats(),
        "cpu": get_cpu_stats(),
    }
