# Langtrace Elastic Demo

This project demonstrates the integration of Langtrace with Elastic APM for tracing AI-powered applications. It uses LangChain, Azure OpenAI, and DuckDuckGo search to create a simple chat interface with AI-assisted responses.

## Prerequisites

- Python 3.8+
- An Azure OpenAI account
- An Elastic APM account

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/bshetti/langhcainChat.git
   cd langtrace
   ```
2. Create and activate a virtual environment:

   ```
   # On macOS and Linux:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows:
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add the following environment variables:

   ```
   # Azure OpenAI settings
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   AZURE_OPENAI_API_VERSION=your_api_version

   # OpenTelemetry settings
   OTEL_EXPORTER_OTLP_ENDPOINT=your_elastic_apm_server_url
   OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your_elastic_apm_secret_token"
   OTEL_SERVICE_NAME=langtrace-elastic-demo
   ```

Note: The OTEL_EXPORTER_OTLP_HEADERS should include the full header string, including the "Authorization=Bearer" prefix.

## Usage

Run the script with:

```
opentelemetry-instrument python langtrace-elastic-demo.py
```

This will start an interactive chat interface. Type your questions and the AI will respond with information from recent web searches.

Type 'quit' to exit the chat.

## Example Trace

![Alt text](/langtrace/img/SCR-20240816-icwt-2.png "a title")

## How it works

1. The script initializes Langtrace with an Elastic APM exporter.
2. It sets up an Azure OpenAI model and a DuckDuckGo search tool.
3. When you ask a question, it performs a web search and uses the results to generate an AI response.
4. All operations are traced using Langtrace, which sends the trace data to Elastic APM.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
