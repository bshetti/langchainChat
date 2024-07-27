import os
from fastapi import FastAPI
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
import asyncio
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource


#set up tracing and initialize
otel_traces_exporter = os.environ.get('OTEL_TRACES_EXPORTER') or 'otlp'
otel_metrics_exporter = os.environ.get('OTEL_TRACES_EXPORTER') or 'otlp'
environment = os.environ.get('ENVIRONMENT') or 'dev'
otel_service_version = os.environ.get('OTEL_SERVICE_VERSION') or '1.0.0'
resource_attributes = os.environ.get('OTEL_RESOURCE_ATTRIBUTES') or 'service.version=1.0,deployment.environment=production'

otel_exporter_otlp_headers = os.environ.get('OTEL_EXPORTER_OTLP_HEADERS')
# fail if secret token not set
if otel_exporter_otlp_headers is None:
    raise Exception('OTEL_EXPORTER_OTLP_HEADERS environment variable not set')
#else:
#    otel_exporter_otlp_fheaders= f"Authorization=Bearer%20{secret_token}"

otel_exporter_otlp_endpoint = os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')
# fail if server url not set
if otel_exporter_otlp_endpoint is None:
    raise Exception('OTEL_EXPORTER_OTLP_ENDPOINT environment variable not set')
else:
    exporter = OTLPSpanExporter(endpoint=otel_exporter_otlp_endpoint, headers=otel_exporter_otlp_headers)


key_value_pairs = resource_attributes.split(',')
result_dict = {}

for pair in key_value_pairs:
    key, value = pair.split('=')
    result_dict[key] = value

resourceAttributes = {
     "service.name": result_dict['service.name'],
     "service.version": result_dict['service.version'],
     "deployment.environment": result_dict['deployment.environment']
#     # Add more attributes as needed
}

resource = Resource.create(resourceAttributes)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("newsQuery")

from opentelemetry.instrumentation.langchain import LangchainInstrumentor
LangchainInstrumentor().instrument()

#from traceloop.sdk import Traceloop
#Traceloop.init(
#  disable_batch=True, 
#  api_key="5e354409db0e2fb83dcc3ebc1e52cff00021eb910a7d76b1db775225a3bfe6e56534335901a6f4e8793b73096be645f7"
#)

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

async def chat_interface():
    print("Welcome to the AI Chat Interface!")
    print("Type 'quit' to exit the chat.")
    
    with tracer.start_as_current_span("getting user query") as span:
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

#manually implement from https://github.com/elastic/observability-examples/blob/main/Elastiflix/python-favorite-otel-manual/main.py