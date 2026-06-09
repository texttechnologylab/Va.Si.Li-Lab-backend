import json
import re
from typing import List, Dict, Any
from models import ToolCall, ToolResult
from tools import BaseTool
from registry import ToolRegistry

class VRAgent:
    def __init__(self, client, registry: ToolRegistry, system_prompt: str, id:str="1111111"):
        self._id = id
        self.client = client
        self.registry = registry
        self.history = []
        self.system_prompt = system_prompt


    def get_tool_count(self):
        return self.registry.get_tool_count()

    def get_id(self):
        return self._id
    
    def set_id(self, id):
        self._id = id
        return True

    def add_tool(self, tool: BaseTool):
        self.registry.register(tool)

    def remove_tool(self, name: str):
        self.registry.remove_tool(name)

    def _build_system_prompt(self) -> str:
        tool_desc = self.registry.get_all_specs()
        return (
            """You are a VR assistant. You have exactly two possible response modes:
1. Normal assistant reply:
- Return plain text only.

2. Tool call:
- Return ONLY a single JSON object.
- No markdown.
- No code fences.
- No explanation before or after.
- The JSON must follow this exact schema:

{"type":"tool_call","id":"<unique string you invent>","name":"<tool name you choose out of the available ones>","arguments":{ ... }}

Rules for tool calls:
- "type" is mandatory and must ALWAYS be exactly "tool_call".
- Never change, translate, or invent another value for "type".
- "id" is mandatory and must be a new unique string chosen by you.
- "name" is mandatory and must be the exact name of the tool you want to call.
- "arguments" is mandatory and must be a JSON object containing the tool arguments.
- If no tool is needed, respond with normal plain text instead of JSON."""
            f"Available tools:\n{tool_desc}"
        )

    def run(self, user_text: str) -> dict:
        prompt = "[AVAILABLE TOOLS]: " + self.registry.get_all_specs() + "\n[USER PROMPT]:" + user_text

        self.history.append({"role": "user", "content": prompt})
        print(prompt)
        system_msg = {"role": "system", "content": self.system_prompt}
        messages = [system_msg] + self.history[-10:]
        response = self.client.chat(messages)

        msg_data = response["choices"][0]["message"]

        print("MSG Data: ", msg_data)

        content = (msg_data.get("content") or "").strip()
        tool_calls = msg_data.get("tool_calls")

        if tool_calls:
            tc = tool_calls[0]
            func_name = tc["function"]["name"]
            raw_args = tc["function"]["arguments"]

            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError as e:
                    return {"reply": f"Tool argument JSON invalid for {func_name}: {e}. Raw: {raw_args}", "is_tool": False, "agent_status": "idle"}
            elif isinstance(raw_args, dict):
                args = raw_args
            else:
                return {"reply": f"Tool argument format invalid for {func_name}: {type(raw_args)}", "is_tool": False, "agent_status": "idle"}

            if (
                isinstance(args, dict)
                and set(args.keys()) == {"arguments"}
                and isinstance(args["arguments"], dict)
            ):
                args = args["arguments"]

            try:
                self.history.append({
                    "role": "assistant",
                    "content": json.dumps({
                        "reply": json.dumps(args),
                        "is_tool": True,
                        "agent_status": "idle"
                    })
                })
                return {
                    "reply": json.dumps(args),
                    "is_tool": True,
                    "agent_status": "idle"
                }
            except Exception as e:
                return {"reply": f"Tool execution failed for {func_name} with args {args}: {e}", "is_tool": False, "agent_status": "idle"}

        # Fallback: only parse pure JSON
        if content.startswith("{") and content.endswith("}"):
            try:
                json.loads(content)
                print("Hallo, ich bin hier!")
                result = {
                    "reply": content,
                    "is_tool": True,
                    "agent_status": "idle"
                }
                self.history.append({"role": "assistant", "content": json.dumps(result)})
                return result
            except Exception as e:
                return {
                    "reply": f"Manual tool JSON invalid: {e}",
                    "is_tool": False,
                    "agent_status": "idle"
                }

        return {
            "reply": content,
            "is_tool": False,
            "agent_status": "idle"
        }