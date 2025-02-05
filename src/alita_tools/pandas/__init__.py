from typing import Any, List, Literal

from langchain_core.tools import BaseToolkit, BaseTool
from pydantic import BaseModel, ConfigDict, create_model
from pydantic.fields import FieldInfo

from .api_wrapper import CSVToolApiWrapper
from ..base.tool import BaseAction

name = "pandas_toolkit"


def get_tools(tool):
    return PandasToolkit().get_toolkit(
        selected_tools=tool['settings'].get('selected_tools', []),
        csv_content=tool['settings'].get('csv_content', None)
    ).get_tools()


class PandasToolkit(BaseToolkit):
    tools: list[BaseTool] = []

    @staticmethod
    def toolkit_config_schema() -> BaseModel:
        available_tools = [
            x['name'] for x in CSVToolApiWrapper.model_construct().get_available_tools()
        ]
        selected_tools = Literal[tuple(available_tools)] if available_tools else Literal[List[str]]

        return create_model(
            name,
            csv_content=(Any, FieldInfo(default=None, title="CSV content", description="CSV content to be processed")),
            selected_tools=(List[str], FieldInfo(default_factory=list, title="Selected tools", description="Selected tools", default=selected_tools)),
            __config__=ConfigDict(json_schema_extra={'metadata': {"label": "Pandas", "icon_url": None}})
        )

    @classmethod
    def get_toolkit(cls, selected_tools: list[str] | None = None, **kwargs):
        if selected_tools is None:
            selected_tools = []
        csv_tool_api_wrapper = CSVToolApiWrapper(**kwargs)
        available_tools = csv_tool_api_wrapper.get_available_tools()
        tools = []
        for tool in available_tools:
            if selected_tools and tool["name"] not in selected_tools:
                continue
            tools.append(BaseAction(
                api_wrapper=csv_tool_api_wrapper,
                name=tool["name"],
                description=tool["description"],
                args_schema=tool["args_schema"]
            ))
        return cls(tools=tools)

    def get_tools(self) -> list[BaseTool]:
        return self.tools