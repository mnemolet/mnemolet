import logging
from pathlib import Path
from typing import Iterator

import torch
from faster_whisper import BatchedInferencePipeline, WhisperModel

from mnemolet.cuore.ingestion.extractors.base import Extractor

logger = logging.getLogger(__name__)


class AudioExtractor(Extractor):
    extensions = {".wav", ".mp3"}

    def __init__(self, model_size="small", buffer_limit=15000):
        super().__init__()  # init from base

        logger.info(f"[audio] Init Whisper model size='{model_size}'")

        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16"
        else:
            device = "cpu"
            compute_type = "int8"

        logger.info(f"[audio] Using device='{device}'")

        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.pipeline = BatchedInferencePipeline(model=self.model)
        # number of chars to accumulate before yeilding
        self.buffer_limit = buffer_limit

    def extract(self, file: Path) -> Iterator[str]:
        logger.info(f"[audio] Starting transcription: {file}'")

        segments, info = self.pipeline.transcribe(str(file), batch_size=16)

        logger.info(
            f"[audio] Language: {info.language}'[audio] Duration: {info.duration:.2f}s'"
        )

        buffer = ""

        for i, segment in enumerate(segments):
            buffer += segment.text.strip() + " "

            if len(buffer) >= self.buffer_limit:
                logger.warning(f"[audio] yielding buffer block: len={len(buffer)}")
                logger.debug(buffer[:300])  # preview first 300 chars
                yield buffer
                buffer = ""
        if buffer:
            logger.warning(f"[audio] yielding FINALbuffer block: len={len(buffer)}")
            logger.debug(buffer[:300])  # preview first 300 chars
            yield buffer

            """
            for i in range(0, len(text), self.chunk_size):
                print(f"TEXT with chunk: {text}")
                yield text[i : i + self.chunk_size]
            """

        logger.info(f"[audio] Finished transcription: {file}")
