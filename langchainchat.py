import os
from fastapi import FastAPI
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
import asyncio

from opentelemetry.instrumentation.langchain import LangchainInstrumentor

LangchainInstrumentor().instrument()


model = AzureChatOpenAI(
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
    azure_deployment=os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'],
    openai_api_version=os.environ['AZURE_OPENAI_API_VERSION'],
)


#initializing duckduckgo
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

wrapper = DuckDuckGoSearchAPIWrapper(region="us-en", time="d", max_results=2)

search = DuckDuckGoSearchResults(api_wrapper=wrapper, source="news")


# Create a prompt template
prompt = PromptTemplate.from_template("""
Human: {human_input}
AI: To answer this query, I'll need to search for some information. Let me do that for you.
{search_result}
Based on this information, here's my response:
""")

# Create the RunnableSequence
chain = RunnableSequence(
    {
        "human_input": lambda x: x["query"],
        "search_result": lambda x: search.run(x["query"]),
    }
    | prompt
    | model
)

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
            result = await chain.ainvoke({"query": user_input})
            print(f"AI: {result.content}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(chat_interface())