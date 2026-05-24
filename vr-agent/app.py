import copy
import os
import requests
import uvicorn
import json
from fastapi import FastAPI, Body
from models import ChatRequest, AgentRequest, ToolAddRemoveRequest
from registry import ToolRegistry
from tools import Load3DObject, GenerateBall, UnityDynamicTool
from agent import VRAgent



app = FastAPI()


API_KEY = os.getenv("API_KEY", "BLA")
API_BASE = os.getenv("API_BASE", "https://lehre.llm.texttechnologylab.org/api")
MODEL = os.getenv("MODEL_NAME", "gondor.gpt-oss:20b")


class LLMClient:
    def chat(self, messages):
        payload = {"model": MODEL, "messages": messages, "temperature": 0.1}
        headers = {"Authorization": f"Bearer {API_KEY}"}
        r = requests.post(f"{API_BASE}/chat/completions", json=payload, headers=headers)
        r.raise_for_status()
        return r.json()


# Global tool registry
registry = ToolRegistry()

agent_dict = {}


@app.post("/createAgent")
def create_agent(request: AgentRequest):
    agent = VRAgent(client=LLMClient(), registry=copy.deepcopy(registry), system_prompt=request.systemPrompt, id=request.id)
    agent_dict[request.id] = agent
    print(f"Created agent with id {request.id}")
    print(f"Count of tools: {agent.get_tool_count()}")


@app.post("/addTool")
def add_tool(request: ToolAddRemoveRequest):
    id = request.id
    tool_name = request.tool_name
    agent = agent_dict[id]
    print(registry.get_tool(tool_name))

    agent.add_tool(registry.get_tool(tool_name))
    print(f"Added tool {tool_name} to agent {id}")
    print(f"Count of tools: {agent.get_tool_count()}")

@app.post("/removeTool")
def remove_tool(request: ToolAddRemoveRequest):
    id = request.id
    tool_name = request.tool_name
    agent = agent_dict[id]
    agent.remove_tool(tool_name)
    print(f"Removed tool {tool_name} from agent {id}")
    print(f"Count of tools: {agent.get_tool_count()}")
    print(f"Global count of tools: {registry.get_tool_count()}")


@app.post("/toolDescriptions")
async def receive_tools(raw_data: str = Body(...)):
    """
    Unity sends a JSON string. We parse it into a list 
    and register each tool dynamically.
    """
    try:
        # 1. Parse the string Unity sent into a Python List
        tools_list = json.loads(raw_data)
        
        for t in tools_list:
            if registry.get_tool(t["name"]) is not None:
                continue

            # 2. Register the tool in our Brain
            dynamic_tool = UnityDynamicTool(
                name=t["name"],
                description=t["description"],
                parameters=t["parameters"]
            )
            registry.register(dynamic_tool)
            print(f"Registered Unity Tool: {t['name']} with parameters {t['parameters']}")

        return {"status": "success", "count": len(tools_list)}
    
    except Exception as e:
        print(f"Error syncing tools: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/chat")
async def chat(request: ChatRequest):
    id = request.id
    print(id)
    try:
        agent = agent_dict[id]
    except KeyError:
        agent = VRAgent(client=LLMClient(), registry=registry, system_prompt="Hallo.", id=id)
        agent_dict[id] = agent

    response_text = agent.run(request.message)

    return response_text

if __name__ == "__main__":
    import sys

    # Check if  "python app.py --server"
    if "--server" in sys.argv:
        print("--- Web Server Mode Activated (For Unity/Docker) ---")
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    else:
        print("--- Terminal Mode Activated ---")
        request = AgentRequest(id="1", systemPrompt="Du bist ein guter Agent.")
        create_agent(request)
        while True:
            u = input("You: ")
            if u.lower() in ["exit", "quit"]: break
            print("Agent:", agent_dict["1"].run(u))
