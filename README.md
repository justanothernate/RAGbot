# SlackRAG

SlackRAG is a simple Slackbot designed to provide automated responses to frequently asked questions within a Slack workspace. It uses text extracted from a `.docx` document as a knowledge base to generate relevant answers using OpenAI's language models. 

## Features

- Extracts information from `.docx` files to create an embeddings `.csv` to serve as a knowledge base.
- Utilizes OpenAI's APIs to understand and respond to queries utilizing the extracted knowledge base for your specific use case.
- Provides an API endpoint for Slack or other apps to POST questions and receive answers.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Slack workspace for integration

### Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/SlackRAG.git
cd SlackRAG
```

Set up a virtual environment and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Export your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY='your_api_key_here'
```

### Usage

1. Prepare your `.docx` document with the source material you want the bot to refernce, using Header 1 formatting to separate sections.

2. Generate the embeddings `.csv` file from your `.docx` document using `docparser.py`. This is what the bot uses to decide what sections are relevant to the query

3. Start the server:

```python slackrag.py
```

4. Test the API with a `curl` command:

```bash
curl -X POST 'http://localhost:4433/ask' -H "Content-Type: application/json" --data '{"query": "What encryption is used on the company's platform?"}'
```
```bash
{"response":"The platform uses TLS 1.3 or 1.2 for encryption in transit."}
```

5. Configure Slack to POST queries to the `/ask` endpoint.

### Tips

It can be helpful to ensure that the source .docx you use to provide the info references the company/platform name when describing it's features so that it's more clear as context what'ss being referred to. i.e. "Company X uses SuperAntiVirus to prevent untreatable infections" is better than "We use SuperAntiVirus...."

You can make this even more explicit by updating the context prompt that's sent to ChatGPT in the `query_message` function to spell out the company/platform name to help it make the association.

This could all be made dynamic by creating embeddings from a GDoc on a regular schedule so `embeddings.csv` always contains the latest updates and can have shared editing.
