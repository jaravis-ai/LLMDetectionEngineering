import os
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional, Literal

from langchain_core.runnables import RunnableConfig

class Configuration(BaseModel):
    """The configurable fields for the Detection Engineering Workflow assistant."""
    llm: Optional[str] = Field(
        #default="gpt-3.5-turbo",
        default="gpt-4o",
        title="LLM Model Name",
        description="The model name to use for the LLM.",
    )
    temperature: Optional[float] = Field(
        default=0.0,
        title="LLM Temperature",
        description="The temperature to use for the LLM.",
    )
    max_retries: Optional[int] = Field(
        default=3,
        title="Max Retries",
        description="The maximum number of retries for the LLM.",
    )
    verbose: Optional[bool] = Field(
        default=True,
        title="Verbose",
        description="Whether to print out the full trace of the LLM calls.",
    )
    langsmith_project: Optional[str] = Field(
        default=os.getenv("LANGSMITH_PROJECT", "new-agent"),
        title="LangSmith Project",
        description="The LangSmith project name to use for tracing.",
    )
    langsmith_api_key: Optional[str] = Field(
        default=os.getenv("LANGSMITH_API_KEY"),
        title="LangSmith API Key",
        description="The LangSmith API key to use for tracing.",
    )

    
    #def to_runnable_config(self) -> RunnableConfig:
    #    return RunnableConfig(
    #        max_retries=self.max_retries,
    #       timeout=None,
    #        tags=None,
    #        metadata=None,
    #       verbose=self.verbose,
    #   )
    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}
        return cls(**values)
    

    #   if config is None:
    #      config = RunnableConfig()
    #    return cls(
    #       max_retries=config.max_retries,
    #        verbose=config.verbose,
    #    )