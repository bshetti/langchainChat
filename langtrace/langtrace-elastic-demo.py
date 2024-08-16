import os
import asyncio
from dotenv import load_dotenv
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from langtrace_python_sdk import langtrace, with_langtrace_root_span
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableSequence
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

# Load environment variables
load_dotenv()

# Elastic APM settings
ELASTIC_APM_SERVER_URL = os.getenv("ELASTIC_APM_SERVER_URL")
SERVICE_NAME = os.getenv("SERVICE_NAME", "langtrace-elastic-demo")
ELASTIC_APM_SECRET_TOKEN = os.getenv("ELASTIC_APM_SECRET_TOKEN")

# Set up Elastic exporter
elastic_exporter = OTLPSpanExporter(
    endpoint=ELASTIC_APM_SERVER_URL,
    headers={"Authorization": f"Bearer {ELASTIC_APM_SECRET_TOKEN}"}
)

# Initialize Langtrace with Elastic exporter
langtrace.init(
    custom_remote_exporter=elastic_exporter,
    batch=True,
    service_name=SERVICE_NAME
)

# Initialize Azure OpenAI model
model = AzureChatOpenAI(
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
    azure_deployment=os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'],
    openai_api_version=os.environ['AZURE_OPENAI_API_VERSION'],
    model="gpt-3.5-turbo"
)

# Initialize DuckDuckGo search
wrapper = DuckDuckGoSearchAPIWrapper(region="us-en", time="d", max_results=2)
search = DuckDuckGoSearchResults(api_wrapper=wrapper, source="news")

# Create a prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Use the provided search results to answer the user's query."),
    ("human", "{human_input}"),
    ("ai", "To answer this query, I'll need to search for some information. Let me do that for you."),
    ("human", "Here are the search results:\n{search_result}"),
    ("ai", "Based on this information, here's my response:")
])

# Create the RunnableSequence
chain = RunnableSequence(
    {
        "human_input": lambda x: x["query"],
        "search_result": lambda x: search.run(x["query"]),
    }
    | prompt
    | model
)

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
            result = await chain.ainvoke({"query": user_input})
            print(f"AI: {result.content}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(chat_interface())
