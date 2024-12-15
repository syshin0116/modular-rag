from abc import ABC, abstractmethod
from typing import Any


class BaseLLMModel(ABC):
    """
    Abstract base class for all large language models (LLMs).
    Defines a unified interface for all LLM implementations.
    """

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text based on the input prompt.

        Args:
            prompt (str): The input prompt for the LLM.
            kwargs (Any): Additional parameters for the generation.

        Returns:
            str: The generated text.
        """
        pass
