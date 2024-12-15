import importlib
from typing import Type, Dict, Any, Tuple
from app.modules.llm_models.base import BaseLLMModel


class LLMModelRegistry:
    """
    Registry for managing LLMs from different providers and models.
    Supports dynamic registration and model creation.
    """

    _registry: Dict[Tuple[str, str], Type[BaseLLMModel]] = {}
    _default_providers: Dict[str, str] = {
        "openai": "langchain.llms.OpenAI",
        "huggingface": "langchain.llms.HuggingFaceHub",
    }

    @classmethod
    def register_model(
        cls, provider: str, model_name: str, model_cls: Type[BaseLLMModel]
    ):
        """
        Register a new LLM model in the registry.

        Args:
            provider (str): The provider of the LLM (e.g., "OpenAI", "HuggingFace").
            model_name (str): The name of the model (e.g., "gpt-4o").
            model_cls (Type[BaseLLMModel]): The class implementing the LLM.
        """
        key = (provider.lower(), model_name.lower())
        cls._registry[key] = model_cls

    @classmethod
    def get_model(cls, provider: str, model_name: str, **kwargs) -> BaseLLMModel:
        """
        Retrieve a registered LLM model or create one dynamically.

        Args:
            provider (str): The provider of the LLM (e.g., "OpenAI").
            model_name (str): The name of the model (e.g., "gpt-4o").
            kwargs (Any): Additional arguments to initialize the model.

        Returns:
            BaseLLMModel: An instance of the requested model.
        """
        key = (provider.lower(), model_name.lower())
        if key in cls._registry:
            return cls._registry[key](**kwargs)

        # If not registered, attempt to dynamically load
        if provider.lower() in cls._default_providers:
            module_path = cls._default_providers[provider.lower()]
            model_cls = cls._dynamic_import(module_path)
            return model_cls(model_name=model_name, **kwargs)

        raise ValueError(
            f"Model '{provider} - {model_name}' is not registered and no dynamic loader found."
        )

    @classmethod
    def list_models(cls) -> list:
        """
        List all registered models.

        Returns:
            list[tuple[str, str]]: A list of (provider, model_name) pairs.
        """
        return [(provider, model) for provider, model in cls._registry.keys()]

    @staticmethod
    def _dynamic_import(module_path: str):
        """
        Dynamically import a module or class.

        Args:
            module_path (str): The Python path of the module or class to import.

        Returns:
            Any: The imported module or class.
        """
        module_name, class_name = module_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
