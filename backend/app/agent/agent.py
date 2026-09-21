"""
agent/agent.py
---------------
The main LangChain agent loop (Multi-Tool Reasoning Engine).

KAISE KAAM KARTA HAI YEH AGENT (Architecture in Hinglish):
  1. Pehle Gemini model banate hain aur usme hamare 3 tools attach (bind) karte hain:
     - search_company_documents (ChromaDB RAG)
     - get_employee_info (Employee database lookup)
     - apply_leave (Leave validation aur database update)
     
  2. Agent ek ReAct-style loop me chalta hai:
     - LLM decide karta hai: User ka answer direct du ya kisi Tool ki zaroorat hai.
     - Agar tool call chahiye, toh hum tool run karte hain aur result wapis LLM ko bhejte hain.
     - Yeh process tab tak chalta hai jab tak LLM final answer generate na kar de.
     
  3. Har turn me conversation history pass hoti hai taaki bot ko purani baatein yaad rahein.
  4. Akhir me response ke sath tools_used aur sources bhi return karte hain.
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

# Maximum tool-calling iterations taaki infinite loop me na fase (safety cap)
MAX_ITERATIONS = 6


def _get_llm_with_tools() -> ChatGoogleGenerativeAI:
    """
    Gemini model initialize karte hain aur tools ko function calling ke liye bind karte hain.
    temperature=0 rakha hai taaki answers deterministic aur reliable rahein (business logic ke liye zaruri).
    """
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_CHAT_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0,   # 0 = No hallucination / factual business response
    )
    # bind_tools() tool ka naam, arguments aur description Gemini ko bhejta hai
    return llm.bind_tools(ALL_TOOLS)


def _execute_tool(tool_call: dict) -> Tuple[str, str]:
    """
    LLM ne jis tool ko bulaya hai, usko execute karte hain.
    Returns: (tool_name, tool_result_as_string)
    """
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    # Tool list me se matching tool dhoondte hain
    tool_fn = next((t for t in ALL_TOOLS if t.name == tool_name), None)

    if not tool_fn:
        logger.error("Agent ne anjaan tool manga: '%s'", tool_name)
        return tool_name, json.dumps({"error": f"Unknown tool: {tool_name}"})

    logger.info("Tool execute ho raha hai: %s | arguments: %s", tool_name, tool_args)

    try:
        # Tool invoke karke result lete hain
        result = tool_fn.invoke(tool_args)
        return tool_name, result
    except Exception as e:
        logger.error("Tool '%s' execute karne me error aaya: %s", tool_name, e, exc_info=True)
        return tool_name, json.dumps({"error": str(e)})


def _extract_sources_from_tool_results(tool_results: List[Dict]) -> List[dict]:
    """
    Tool ke results me se cited source documents nikalte hain.
    Sirf search_company_documents tool hi documents ke sources return karta hai.
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
    Single user message ke liye agent ko run karta hai.

    Args:
        employee_id:     User ka employee ID (jaise 'EMP001')
        user_message:    User ka natural language question
        conversation_id: Previous chat continue karne ke liye unique session ID

    Returns:
        Dictionary: { answer, sources, tools_used, conversation_id }
    """
    # Agar pehle se conversation ID nahi hai toh naya create karo
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        logger.info("Nayi conversation shuru hui: '%s'", conversation_id)
    else:
        logger.info("Purani conversation continue ho rahi hai: '%s'", conversation_id)

    # In-memory history se pichle messages load karte hain
    history: List[BaseMessage] = get_history(conversation_id)

    # Dynamic system prompt banate hain (aaj ki date aur employee ID ke sath)
    system_prompt = build_agent_system_prompt(
        employee_id=employee_id,
        today_date=date.today().isoformat(),
    )

    # LLM ke liye message sequence tayar karte hain:
    # [SystemMessage, ...purane messages..., HumanMessage(aaj ka)]
    messages: List[BaseMessage] = [
        SystemMessage(content=system_prompt),
        *history,
        HumanMessage(content=user_message),
    ]

    llm_with_tools = _get_llm_with_tools()

    tools_used: List[str] = []
    tool_results: List[Dict] = []
    iterations = 0

    # ── ReAct Agent Loop ────────────────────────────────────────────────────
    # Yeh loop tab tak chalega jab tak LLM direct answer na de de ya MAX_ITERATIONS na poori ho jayein
    while iterations < MAX_ITERATIONS:
        iterations += 1
        logger.debug("Agent loop iteration: %d", iterations)

        # Gemini ko message bhejte hain
        response: AIMessage = llm_with_tools.invoke(messages)
        messages.append(response)

        # Agar Gemini ne koi tool call nahi kiya, matlab final answer mil gaya!
        if not response.tool_calls:
            logger.info(
                "Agent ne %d iterations me answer finalize kiya. Tools used: %s",
                iterations, tools_used,
            )
            break

        # Agar Gemini ne tools call kiye hain toh unhe baari baari execute karte hain
        for tool_call in response.tool_calls:
            tool_name, tool_result = _execute_tool(tool_call)

            if tool_name not in tools_used:
                tools_used.append(tool_name)

            tool_results.append({
                "tool_name": tool_name,
                "result": tool_result,
            })

            # Tool ka result ToolMessage ke roop me wapis LLM history me jodte hain
            messages.append(
                ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=tool_result,
                )
            )

    else:
        # Safety fallback: Agar 6 iterations cross ho gaye toh zabardasti final response generate karate hain
        logger.warning("Max iterations cross ho gaye. Forcing final answer.")
        final_response = llm_with_tools.invoke(messages)
        messages.append(final_response)
        response = final_response

    # Final response ka text extract karte hain
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

    # RAG tool results me se cited source documents extract karte hain
    sources = _extract_sources_from_tool_results(tool_results)

    # Chat history save karte hain (SystemMessage ko chhodkar, taaki history clean rahe)
    non_system_messages = [m for m in messages if not isinstance(m, SystemMessage)]
    save_history(conversation_id, non_system_messages)

    logger.info(
        "Final response tayar hai | conv=%s | tools=%s | sources=%d",
        conversation_id, tools_used, len(sources),
    )

    return {
        "answer": answer,
        "sources": sources,
        "tools_used": tools_used,
        "conversation_id": conversation_id,
    }
