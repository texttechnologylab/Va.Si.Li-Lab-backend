from pydantic import BaseModel
from typing import Dict, Any, Optional

class ToolCall(BaseModel):
    id: int
    name: str
    arguments: Dict[str, Any]

class ToolResult(BaseModel):
    id: str
    ok: bool
    result: str
    error: Optional[str] = ""

class ChatRequest(BaseModel):
    id:str
    message: str

class AgentRequest(BaseModel):
    id: str
    systemPrompt: str

class ToolAddRemoveRequest(BaseModel):
    id: str
    tool_name: str