from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from typing import List, Dict, Any
"""Data Science Agent V2: generate nl2py and use code interpreter to run the code."""
import os
from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.agents import Agent
from .prompts import return_instructions_ds


ds_agent = Agent(
    #model=os.getenv("ANALYTICS_AGENT_MODEL"),
    model="gemini-2.0-flash",
    name="data_science_agent",
    instruction=return_instructions_ds(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
)

async def call_ds_agent(
    question: str,
    query_result: List[Dict[str, Any]],
    tool_context: ToolContext
) -> str: # <-- We return a simple string, as your original file did.

    """
    Tool to call data science (nl2py) agent.
    This tool returns a text summary.
    The sub-agent it calls (ds_agent) will create an image artifact in the context
    as a side-effect.
    """

    ds_agent_output = ""
    if query_result is None:
        return "Error: You must run a query and get a 'query_result' before you can call call_ds_agent."

    question_with_data = f"""
        Question to answer: {question}

        Here is the data to use:
        {query_result}

    """
    print("[tools.py] Calling DS Agent with data...")

    agent_tool = AgentTool(agent=ds_agent)

    # The sub-agent will return text and add an artifact to the context
    # as a side-effect. We only need to capture the text output.
    ds_agent_output = await agent_tool.run_async(
        args={"request": question_with_data},
        tool_context=tool_context
    )

    print(f"[tools.py] DS Agent finished. Text output: {ds_agent_output}")

    # Just return the text. The main agent will handle the artifact.
    return ds_agent_output

