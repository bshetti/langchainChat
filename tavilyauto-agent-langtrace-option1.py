import os
from langchain-openai import AzureChatOpenAI
import asyncio

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

langtrace.init(
  batch=True,
)

model = AzureChatOpenAI(
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
    azure_deployment=os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'],
    openai_api_version=os.environ['AZURE_OPENAI_API_VERSION'],
)

#initializing tavily
from langchain_community.tools.tavily_search import TavilySearchResults

search = TavilySearchResults(max_results=2)

toolxs = [search]

model_with_tools = model.bind_tools(toolxs)


from langchain.agents import create_tool_calling_agent
from langchain import hub

# Create a prompt template
prompt = hub.pull("hwchase17/openai-functions-agent")
prompt.messages

agent = create_tool_calling_agent(model, toolxs, prompt)

from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(agent=agent, tools=toolxs, verbose=True)

@with_langtrace_root_span()
async def chat_interface():
    print("Welcome to the AI Chat Interface!")
    print("Type 'quit' to exit the chat.")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            print("Thank you for chatting. Goodbye!")
            break
    
        print("AI: Thinking...")
        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"AI: {result['output']}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(chat_interface())
