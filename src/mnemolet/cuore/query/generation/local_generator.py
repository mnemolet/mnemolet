import json
import logging
from dataclasses import dataclass
from typing import Generator

import requests

logger = logging.getLogger(__name__)


@dataclass
class LocalGeneratorConfig:
    url: str
    model: str
    prompt: str


class LocalGenerator:
    """
    Generate an answer using local LLM (via Ollama API).
    """

    def __init__(self, cfg: LocalGeneratorConfig):
        self.cfg = cfg

    def generate_answer(
        self, query: str, context_chunks: list[str]
    ) -> Generator[str, None, None]:
        """
        Generate an answer.
        """
        if not context_chunks:
            context = (
                "No additional context provided. Answer using your general knowledge."
            )
        else:
            context = "\n\n".join(context_chunks)

        # prompt = f"Context:\n{context}\n\nQuestion:\n{query}\n\n:"
        prompt = f"""
        {self.cfg.prompt}

        ### Reference context
        {context}

        ---

        ### Question
        {query}

        ### Assitant Response:
        """

        payload = {
            "model": self.cfg.model,
            "prompt": prompt,
            "stream": True,
            "options": {"keep_alive": "10m"},
        }

        try:
            response = requests.post(
                f"{self.cfg.url}/api/generate", json=payload, stream=True
            )
            response.raise_for_status()  # raise for non 200 status

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                try:
                    chunk = json.loads(line)

                    if "response" in chunk:
                        yield chunk["response"]

                    if chunk.get("done"):
                        break

                except json.JSONDecodeError as e:
                    logger.error(
                        f"JSON decode failed: {e}. Raw response: {response.text[:1000]}"
                    )
                    raise RuntimeError(f"Invalid JSON response from Ollama: {e}") from e
                    continue
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise RuntimeError(f"Failed to generate answer: {e}") from e


def get_llm_generator(url: str, model: str, prompt: str) -> LocalGenerator:
    cfg = LocalGeneratorConfig(
        url=url,
        model=model,
        prompt=prompt,
    )
    return LocalGenerator(cfg)
