# # app.py
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os
# import uuid
# import logging
# import json
# import sys
# from dotenv import load_dotenv
# from mcp import ClientSession, StdioServerParameters
# from mcp.types import ListToolsResult
# from mcp.client.stdio import stdio_client
# from mcp.cli.claude import get_claude_config_path
# from contextlib import asynccontextmanager
# from dataclasses import dataclass
# from typing import List
# import asyncio


# # Configure logging
# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes


# # Get Anthropic API key from environment or config
# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# if not ANTHROPIC_API_KEY:
#     logger.warning(
#         "ANTHROPIC_API_KEY not found in environment or Claude config. Some features may not work."
#     )

# # Dictionary to store active MCP sessions
# active_sessions = {}


# @app.route("/api/config", methods=["GET"])
# def get_config():
#     """Get sanitized configuration information (no API keys)."""
#     return jsonify(
#         {
#             "apiKeyConfigured": bool(ANTHROPIC_API_KEY),
#         }
#     )


# @app.route("/api/session", methods=["POST"])
# def create_session():
#     """Create a new MCP session with the specified model."""
#     try:
#         if not ANTHROPIC_API_KEY:
#             return (
#                 jsonify(
#                     {
#                         "error": "API key not configured. Please check your environment or Claude config."
#                     }
#                 ),
#                 500,
#             )

#         data = request.json
#         model_id = data.get("model_id", "claude-3-7-sonnet-20250219")

#         logger.info(f"Creating new MCP session with model: {model_id}")

#         # Create an MCP session
#         # Generate a session ID for the frontend
#         session_id = str(uuid.uuid4())

#         # Store the session
#         active_sessions[session_id] = {
#             "session": {},
#             "model_id": model_id,
#             "messages": [],
#         }

#         logger.info(f"Created MCP session: {session_id}")

#         return jsonify({"session_id": session_id, "model_id": model_id, "messages": []})

#     except Exception as e:
#         logger.error(f"Error creating MCP session: {str(e)}")
#         return jsonify({"error": str(e)}), 500


# @app.route("/api/session/<session_id>/message", methods=["POST"])
# def send_message(session_id):
#     """Send a message in an existing MCP session."""
#     try:
#         if session_id not in active_sessions:
#             return jsonify({"error": "Session not found"}), 404

#         data = request.json
#         message = data.get("message", "")

#         if not message:
#             return jsonify({"error": "Message cannot be empty"}), 400

#         logger.info(f"Sending message in MCP session {session_id}: {message[:50]}...")

#         # Get the session
#         session_data = active_sessions[session_id]

#         # Store user message
#         session_data["messages"].append(
#             {"role": "user", "content": message, "timestamp": str(uuid.uuid1())}
#         )

#         # Send message to Claude via MCP
#         # response = session.send_message(message)
#         response = "hello"

#         # Store assistant response
#         session_data["messages"].append(
#             {"role": "assistant", "content": response, "timestamp": str(uuid.uuid1())}
#         )

#         return jsonify({"response": response, "message_id": str(uuid.uuid4())})

#     except Exception as e:
#         logger.error(f"Error sending message to MCP: {str(e)}")
#         return jsonify({"error": str(e)}), 500


# @app.route("/api/session/<session_id>", methods=["GET"])
# def get_session(session_id):
#     """Get details about an existing session."""
#     try:
#         if session_id not in active_sessions:
#             return jsonify({"error": "Session not found"}), 404

#         session_data = active_sessions[session_id]

#         return jsonify(
#             {
#                 "session_id": session_id,
#                 "model_id": session_data["model_id"],
#                 "messages": session_data["messages"],
#             }
#         )

#     except Exception as e:
#         logger.error(f"Error getting session: {str(e)}")
#         return jsonify({"error": str(e)}), 500


# @app.route("/api/session/<session_id>", methods=["DELETE"])
# def end_session(session_id):
#     """End an existing MCP session."""
#     try:
#         if session_id not in active_sessions:
#             return jsonify({"error": "Session not found"}), 404

#         logger.info(f"Ending MCP session: {session_id}")

#         # Get the session
#         session_data = active_sessions[session_id]
#         session = session_data["session"]

#         # Clean up the session
#         try:
#             session.close()
#         except Exception as e:
#             logger.warning(f"Error closing MCP session: {str(e)}")

#         # Remove from active sessions
#         del active_sessions[session_id]

#         return jsonify({"success": True})

#     except Exception as e:
#         logger.error(f"Error ending session: {str(e)}")
#         return jsonify({"error": str(e)}), 500


# @app.route("/api/models", methods=["GET"])
# def get_models():
#     """Get available Claude models."""
#     return jsonify(
#         {
#             "models": [
#                 {"id": "claude-3-7-sonnet-20250219", "name": "Claude 3.7 Sonnet"},
#                 {"id": "claude-3-5-sonnet-20240620", "name": "Claude 3.5 Sonnet"},
#                 {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
#                 {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
#             ]
#         }
#     )


# @app.route("/api/health", methods=["GET"])
# def health_check():
#     """Health check endpoint."""
#     return jsonify(
#         {
#             "status": ("healthy" if ANTHROPIC_API_KEY else "unhealthy"),
#             "active_sessions": len(active_sessions),
#             "api_key_configured": bool(ANTHROPIC_API_KEY),
#         }
#     )


# @dataclass
# class MCPSessionWrapper:
#     tools: ListToolsResult
#     session: ClientSession
#     prompt: str


# @asynccontextmanager
# async def launch_mcp_server(name):
#     config = json.load(get_claude_config_path().open())
#     cmd = config["mcpServers"][name]["command"]
#     args = config["mcpServers"][name].get("args")
#     env = config["mcpServers"][name].get("env")
#     params = StdioServerParameters(command=cmd, args=args, env=env)
#     async with (
#         stdio_client(params) as (read, write),
#         ClientSession(read, write) as mcp_session,
#     ):
#         await mcp_session.initialize()
#         tools = await mcp_session.list_tools()
#         prompt = None
#         if prompts := await mcp_session.list_prompts():
#             for pname in prompts.prompts:
#                 if pname == "system_prompt":
#                     if (
#                         pv := await mcp_session.get_prompt(pname)
#                     ) is not None and pv.messages:
#                         prompt = "\n".join(
#                             pm.content.text
#                             for pm in pv.messages
#                             if pm.content.type == "text"
#                         )
#                     break
#         yield MCPSessionWrapper(tools, mcp_session, prompt)


# async def start_server(mcp_session):
#     port = int(os.getenv("PORT", 5566))
#     debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

#     logger.info(f"Starting server on port {port}, debug={debug}")
#     logger.info(f"API key configured: {bool(ANTHROPIC_API_KEY)}")
#     logger.info(f"MCP module available: {'mcp' in sys.modules}")
#     app.config["mcp_session"] = mcp_session
#     app.run(host="0.0.0.0", port=port, debug=debug)


# async def main():
#     async with launch_mcp_server("Dremio") as mcp_session:
#         await start_server(mcp_session)


# if __name__ == "__main__":
#     asyncio.run(main())

from dremioai.servers.frameworks.beeai import server
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from flask.views import MethodView
from flask import Flask, request, jsonify

app = Flask(__name__)


class ChatAPI(MethodView):
    def __init__(self, agent: server.ReactAgentWithSession):
        self.agent = agent
        super().__init__()

    def post(self):
        # result = self.agent.agent.run(request["message"])
        return jsonify({"result": "hello"})

    _inst = None

    @classmethod
    def instance(cls):
        if cls._inst is None:
            cls._inst = ChatAPI.as_view("chat")
        return cls._inst

    @classmethod
    def register(cls, app: Flask):
        app.add_url_rule("/api/chat", view_func=cls.instance())


@asynccontextmanager
async def create_react_agent() -> AsyncGenerator[server.ReactAgentWithSession, None]:
    async with server.create_react_agent() as agent:
        yield agent


def start_server(agent: server.ReactAgentWithSession):
    ChatAPI.register(app)
    app.run(host="0.0.0.0", port=5566, debug=True)


async def main():
    async with create_react_agent() as agent:
        start_server(agent)


if __name__ == "__main__":
    asyncio.run(main())
