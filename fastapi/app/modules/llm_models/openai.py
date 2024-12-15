from typing import Any, List, Generator
from langchain_openai.llms.base import OpenAI
from app.modules.llm_models.base import BaseLLMModel


class OpenAILLM(BaseLLMModel):
    """
    OpenAI LLM implementation using LangChain's ChatOpenAI wrapper.
    """

    def __init__(self, model_name: str, api_key: str, **kwargs: Any):
        """
        Initialize the OpenAI LLM.

        Args:
            model_name (str): The name of the OpenAI model (e.g., "gpt-4o").
            api_key (str): The OpenAI API key for authentication.
            kwargs (Any): Additional configuration for the model.
        """
        self.model_name = model_name
        self.api_key = api_key
        self.config = kwargs
        self.llm = OpenAI(
            model=model_name,
            openai_api_key=api_key,
            **kwargs,
        )

    def generate(
        self, prompts: List[str], stream: bool = False, **kwargs: Any
    ) -> Generator[str, None, None] | str:
        """
        Generate text using the OpenAI model.

        Args:
            prompts (List[str]): List of input prompts for the model.
            stream (bool): Whether to stream the response (not directly supported here).
            kwargs (Any): Additional parameters for the OpenAI API.

        Returns:
            Generator[str, None, None] | str: The generated text.
        """
        if len(prompts) != 1:
            raise ValueError("Only single prompt is supported.")

        prompt = prompts[0]
        try:
            if stream:
                raise NotImplementedError(
                    "Streaming is not supported in this implementation."
                )
            else:
                response = self.llm.predict(prompt)
                return response
        except Exception as e:
            raise RuntimeError(f"Error in LangChain OpenAI LLM: {str(e)}")

    def configure(self, **kwargs: Any):
        """
        Update the configuration of the model.

        Args:
            kwargs (Any): Parameters to update the model configuration.
        """
        self.config.update(kwargs)
        self.llm = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.api_key,
            **self.config,
        )
