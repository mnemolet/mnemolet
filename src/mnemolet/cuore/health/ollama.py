import logging

import requests

logger = logging.getLogger(__name__)


def get_ollama_status(ollama_url: str) -> dict:
    """
    Returns:
        {
            "running": bool,
            "version": str | None
        }
    """
    try:
        url = f"{ollama_url}/api/version"
        x = requests.get(url, timeout=1)
        if x.status_code == 200:
            data = x.json()
            return {
                "running": True,
                "version": data.get("version"),
            }
    except Exception as e:
        logger.debug(f"Failed to connect to Ollama over {ollama_url}: {e}")

    return {
        "running": False,
        "version": None,
    }
