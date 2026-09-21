"""
agent/agent.py
---------------
The main LangChain agent.

HOW THE AGENT WORKS:
  1. We create a Gemini chat model with our three tools bound to it.
     (bind_tools tells Gemini about the tool signatures via function calling.)
  
  2. The agent runs in a ReAct-style loop:
       - LLM decides: answer directly OR call a tool.
       - If a tool is called, we execute it and feed the result back to the LLM.
       - Loop repeats until the LLM produces a final answer (no more tool calls).
  
  3. The conversation history is passed on every call so the LLM has context.
  
  4. We track which tools were called and which sources were cited.

WHY NOT A PRE-BUILT LangChain AGENT EXECUTOR?
  The newer LangChain approach (create_react_agent, etc.) uses LangGraph under the hood.
  We implement the loop manually here so it's easy to understand and debug —
  perfect for a fresher to explain in an interview.
"""

import json
import logging
import uuid
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.agent.state import get_history, save_history
from app.config import settings
from app.prompts.agent_prompts import build_agent_system_prompt
from app.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# Maximum number of tool-calling iterations before we force a final answer
MAX_ITERATIONS = 6


def _get_llm_with_tools() -> ChatGoogleGenerativeAI:
    """
    Create the Gemini chat model with tools bound to it.
    
    bind_tools() sends the tool schemas to Gemini so it knows:
    - What tools exist
    - What arguments each tool expects
    - When to call them (based on the docstrings we wrote)
    """
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_CHAT_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0,   # 0 = deterministic, no creativity — important for business logic
    )
    return llm.bind_tools(ALL_TOOLS)


def _execute_tool(tool_call: dict) -> Tuple[str, str]:
    """
    Execute a single tool call returned by the LLM.

    Returns:
        (tool_name, result_string)
    """
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    # Find the matching tool object
    tool_fn = next((t for t in ALL_TOOLS if t.name == tool_name), None)

    if not tool_fn:
        logger.error("Agent requested unknown tool: '%s'", tool_name)
        return tool_name, json.dumps({"error": f"Unknown tool: {tool_name}"})

    logger.info("Executing tool: %s | args: %s", tool_name, tool_args)

    try:
        result = tool_fn.invoke(tool_args)
        return tool_name, result
    except Exception as e:
        logger.error("Tool '%s' raised an exception: %s", tool_name, e, exc_info=True)
        return tool_name, json.dumps({"error": str(e)})


def _extract_sources_from_tool_results(tool_results: List[Dict]) -> List[dict]:
    """
    Parse tool results to extract source citations.
    Only search_company_documents returns sources.
    """
    sources = []
    seen = set()

    for tr in tool_results:
        if tr["tool_name"] != "search_company_documents":
            continue
        try:
            data = json.loads(tr["result"])
            for s in data.get("sources", []):
                key = (s.get("source"), s.get("page"))
                if key not in seen:
                    seen.add(key)
                    sources.append(s)
        except (json.JSONDecodeError, AttributeError):
            pass

    return sources


def run_agent(
    employee_id: str,
    user_message: str,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the agent for a single user message.

    Args:
        employee_id:     The employee's ID (used in the system prompt)
        user_message:    The user's input
        conversation_id: If provided, continues an existing conversation

    Returns:
        A dict with: answer, sources, tools_used, conversation_id
    """
    # Create or reuse conversation ID
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        logger.info("New conversation started: '%s'", conversation_id)
    else:
        logger.info("Continuing conversation: '%s'", conversation_id)

    # Load history
    history: List[BaseMessage] = get_history(conversation_id)

    # Build the system prompt with today's date and employee context
    system_prompt = build_agent_system_prompt(
        employee_id=employee_id,
        today_date=date.today().isoformat(),
    )

    # Construct the messages list:
    # [SystemMessage, ...history..., HumanMessage(current)]
    messages: List[BaseMessage] = [
        SystemMessage(content=system_prompt),
        *history,
        HumanMessage(content=user_message),
    ]

    llm_with_tools = _get_llm_with_tools()

    tools_used: List[str] = []
    tool_results: List[Dict] = []
    iterations = 0

    # ── Agent loop ──────────────────────────────────────────────────────────
    # This loop continues until:
    #   (a) The LLM produces a final text answer (no tool_calls), OR
    #   (b) We hit MAX_ITERATIONS (safety limit)

    while iterations < MAX_ITERATIONS:
        iterations += 1
        logger.debug("Agent iteration %d", iterations)

        # Send messages to Gemini
        response: AIMessage = llm_with_tools.invoke(messages)
        messages.append(response)

        # Check if Gemini wants to call tools
        if not response.tool_calls:
            # No tool calls → this is the final answer
            logger.info(
                "Agent finished after %d iteration(s). Tools used: %s",
                iterations, tools_used,
            )
            break

        # Process each tool call
        for tool_call in response.tool_calls:
            tool_name, tool_result = _execute_tool(tool_call)

            if tool_name not in tools_used:
                tools_used.append(tool_name)

            tool_results.append({
                "tool_name": tool_name,
                "result": tool_result,
            })

            # Add the tool result back to the message list
            messages.append(
                ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=tool_result,
                )
            )

    else:
        # Safety: if we hit MAX_ITERATIONS, ask LLM for a final answer anyway
        logger.warning("Max iterations reached. Forcing final answer.")
        final_response = llm_with_tools.invoke(messages)
        messages.append(final_response)
        response = final_response

    # Extract the final answer text
    if isinstance(response.content, str):
        answer = response.content
    elif isinstance(response.content, list):
        text_parts = []
        for part in response.content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif hasattr(part, "text"):
                text_parts.append(str(part.text))
            else:
                text_parts.append(str(part))
        answer = "".join(text_parts)
    else:
        answer = str(response.content)

    # Extract sources from RAG tool results
    sources = _extract_sources_from_tool_results(tool_results)

    # Save updated conversation history (without the system message — it's rebuilt each time)
    # We save only non-system messages to keep history clean
    non_system_messages = [m for m in messages if not isinstance(m, SystemMessage)]
    save_history(conversation_id, non_system_messages)

    logger.info(
        "Response ready | conv=%s | tools=%s | sources=%d",
        conversation_id, tools_used, len(sources),
    )

    return {
        "answer": answer,
        "sources": sources,
        "tools_used": tools_used,
        "conversation_id": conversation_id,
    }
