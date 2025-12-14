import logging

from mnemolet.cuore.query.generation.generate_answer import generate_answer
from mnemolet.cuore.query.generation.local_generator import LocalGenerator
from mnemolet.cuore.query.retrieval.retriever import Retriever

logger = logging.getLogger(__name__)


class ChatSession:
    def __init__(
        self,
        retriever: Retriever,
        generator: LocalGenerator,
    ):
        self.history = []
        self.retriever = retriever
        self.generator = generator

    def ask(self, query: str):
        results = []
        full_prompt = query

        if self.history:
            full_prompt = self.build_context(query)

        for chunk, sources in generate_answer(
            retriever=self.retriever,
            generator=self.generator,
            query=full_prompt,
            chat=True,
        ):
            if sources is None:
                # live streaming
                yield chunk
                results.append(chunk)

        print()

        # save full response in history
        answer = "".join(results)
        self.history.append({"role": "user", "message": query})
        self.history.append(
            {"role": "assistant", "message": answer, "sources": sources or []}
        )

        return answer

    def append_to_history(self, role: str, content: str):
        """
        Add a context from the saved history.
        """
        self.history.append(
            {
                "role": role,
                "message": content,
            }
        )

    def build_context(self, query: str):
        if logger.isEnabledFor(logging.DEBUG):
            for i, m in enumerate(self.history):
                logger.debug(f"History item: {i}, {m}")

        context = ""
        for m in self.history:
            role = m["role"]
            content = m["message"]
            context += f"{role}: {content}\n"

        context += f"user: {query}\n"
        return context

    def load_history(self, messages):
        for m in messages:
            self.append_to_history(m["role"], m["message"])
