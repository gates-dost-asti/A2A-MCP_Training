from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from typing import List, Dict, TypedDict
import asyncio
import json
from gates_openai import create_response
from contextlib import AsyncExitStack
import traceback


class ToolDefinition(TypedDict):
    type: str
    name: str
    description: str
    parameters: dict

class MCP_ChatBot:

    def __init__(self):
        self.sessions: List[ClientSession] = [] 
        self.exit_stack = AsyncExitStack() 
        self.available_tools: List[ToolDefinition] = []
        self.available_prompts = []
        self.tool_to_session: Dict[str, ClientSession] = {}

    async def connect_to_server(self, server_name: str, server_config: dict) -> None:
        """Connect to a single MCP server."""
        try:

            transport = server_config.get("transport", "stdio")
            if transport == "sse":
                url = server_config["url"]
                read, write = await self.exit_stack.enter_async_context(sse_client(url))
            else:
                server_params = StdioServerParameters(**server_config)
                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                ) # new
                read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )

            await session.initialize()
            self.sessions.append(session)

            try:
                # List available tools for this session
                response = await session.list_tools()
                tools = response.tools
                print(f"\nConnected to {server_name} with tools:", [tool.name for tool in tools])
                for tool in tools:
                    self.tool_to_session[tool.name] = session
                    self.available_tools.append({
                        "type": "function",
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    })

                # List available prompts
                prompts_response = await session.list_prompts()
                if prompts_response and prompts_response.prompts:
                    for prompt in prompts_response.prompts:
                        self.tool_to_session[prompt.name] = session
                        self.available_prompts.append({
                            "name": prompt.name,
                            "description": prompt.description,
                            "arguments": prompt.arguments
                        })
                # List available resources
                resources_response = await session.list_resources()
                if resources_response and resources_response.resources:
                    for resource in resources_response.resources:
                        resource_uri = str(resource.uri)
                        self.tool_to_session[resource_uri] = session      

            except Exception as e:
                print(f"Error {e}")    

        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")
            traceback.print_exc()


    async def connect_to_servers(self): #new
        """Connect to all configured MCP servers."""
        try:
            with open("server_config.json", "r") as file:
                data = json.load(file)
            servers = data.get("mcpServers", {})

            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)

        except Exception as e:
            print(f"Error loading server configuration: {e}")
            raise



    async def process_query(self, query: str = None, previous_response_id: str = None):

        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant.
                Use search_papers tool to search for academic papers on a given topic on arxiv.
                User extract_info tool to get more information on papers retrieved through the search_papers tool.
                """
            },
            {
                "role":"user",
                "content":query
            }
        ]

        kwargs = {}

        if previous_response_id:
            kwargs["previous_response_id"] = previous_response_id

        response = create_response(
            model = "gpt-4o-mini",
            tools = self.available_tools,
            input = messages,
            **kwargs
        )

        function_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            return response.output_text, response.id

        tool_outputs = []

        while True:

            for call in function_calls:

                tool_name = call.name
                tool_args = json.loads(call.arguments)

                session = self.tool_to_session[tool_name]
                result = await session.call_tool(tool_name, arguments = tool_args)
                tool_output = "\n".join(map(str, result))
                # print(tool_output)

                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": tool_output
                })

            messages.extend(tool_outputs)

            response = create_response(
                model = "gpt-4o-mini",
                input = tool_outputs,
                tools = self.available_tools,
                previous_response_id = response.id
            )


            function_calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if function_calls:
                print("Function calls found...")
                continue
            else:
                return response.output_text, response.id


    async def get_resource(self, resource_uri):
        session = self.tool_to_session.get(resource_uri)
        
        # Fallback for papers URIs - try any papers resource session
        if not session and resource_uri.startswith("papers://"):
            for uri, sess in self.tool_to_session.items():
                if uri.startswith("papers://"):
                    session = sess
                    break
            
        if not session:
            print(f"Resource '{resource_uri}' not found.")
            return
        
        try:
            result = await session.read_resource(uri=resource_uri)
            if result and result.contents:
                print(f"\nResource: {resource_uri}")
                print("Content:")
                print(result.contents[0].text)
            else:
                print("No content available.")
        except Exception as e:
            print(f"Error: {e}")
    
    async def list_prompts(self):
        """List all available prompts."""
        if not self.available_prompts:
            print("No prompts available.")
            return
        
        print("\nAvailable prompts:")
        for prompt in self.available_prompts:
            print(f"- {prompt['name']}: {prompt['description']}")
            if prompt['arguments']:
                print(f"  Arguments:")
                for arg in prompt['arguments']:
                    arg_name = arg.name if hasattr(arg, 'name') else arg.get('name', '')
                    print(f"    - {arg_name}")
    
    async def execute_prompt(self, prompt_name, args, previous_response_id):
        """Execute a prompt with the given arguments."""
        session = self.tool_to_session.get(prompt_name)
        if not session:
            print(f"Prompt '{prompt_name}' not found.")
            return
        
        try:
            result = await session.get_prompt(prompt_name, arguments=args)
            if result and result.messages:
                prompt_content = result.messages[0].content
                
                # Extract text from content (handles different formats)
                if isinstance(prompt_content, str):
                    text = prompt_content
                elif hasattr(prompt_content, 'text'):
                    text = prompt_content.text
                else:
                    # Handle list of content items
                    text = " ".join(item.text if hasattr(item, 'text') else str(item) 
                                  for item in prompt_content)
                
                print(f"\nExecuting prompt '{prompt_name}'...")
                response, response_id = await self.process_query(text, previous_response_id)
                return response, response_id
        except Exception as e:
            print(f"Error: {e}")

    async def chat_loop(self):
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        print("Use @folders to see available topics")
        print("Use @<topic> to search papers in that topic")
        print("Use /prompts to list available prompts")
        print("Use /prompt <name> <arg1=value1> to execute a prompt")
        response_id = None
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break

                # Check for @resource syntax first
                if query.startswith('@'):
                    # Remove @ sign  
                    topic = query[1:]
                    if topic == "folders":
                        resource_uri = "papers://folders"
                    else:
                        resource_uri = f"papers://{topic}"
                    await self.get_resource(resource_uri)
                    continue
                
                # Check for /command syntax
                if query.startswith('/'):
                    parts = query.split()
                    command = parts[0].lower()

                    if command == '/prompts':
                        await self.list_prompts()
                    elif command == '/prompt':
                        if len(parts) < 2:
                            print("Usage: /prompt <name> <arg1=value1> <arg2=value2> ...")
                            continue

                        prompt_name = parts[1]
                        args = {}

                        # parse arguments
                        ctr=2
                        for arg in parts[2:]:
                            print(f"parts[{ctr}]: {arg}")
                            if '=' in arg and ctr <= len(parts):
                                key, value = arg.split('=',1)
                                added = 0
                                while ctr<len(parts)-1:
                                    added += 1
                                    ctr += 1   
                                    #print(f"next to {parts[ctr-1]} is {parts[ctr]}")
                                    if '=' not in parts[ctr]: 
                                        value += " " + parts[ctr]
                                        print(value)
                                    else:
                                        ctr -= added
                                        break
                                args[key] = value
                            ctr += 1 

                        response, response_id = await self.execute_prompt(prompt_name, args, response_id)
                        print("\n")
                        print(response)
                    else:
                        print(f"Unknown command: {command}")
                    continue

                response, response_id = await self.process_query(query, response_id)

                print("\n")
                print(response)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Cleanly close all resources using AsyncExitStack"""
        await self.exit_stack.aclose()



async def main():
    chatbot = MCP_ChatBot()
    try:
        await chatbot.connect_to_servers()
        await chatbot.chat_loop()
    finally:
        await chatbot.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
