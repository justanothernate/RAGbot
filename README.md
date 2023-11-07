# SlackRAG
A simple Slackbot that can answer questions based on text in a file. This can be helpful to enable a bot to answer frequently asked questions that hit you or your team.

# To use
Get a document you want to use as the source for your answers. This should be in .docx format as it's currently setup with sections broken up using Header 1 formatting.

Use docparser.py to create an embeddings .csv of your .docx file that SlackRAG will use to help answer questions.

You'll need to setup your OpenAI API key as an enviornment variable for this to authenticate.

Once you have it setup, you can test that it's working properly by querying against information that you have in your docx file with the below:

curl -X POST 'localhost:4433/ask' -H "Content-Type: application/json" --data '{"query": "Tell me something about X"}'

After that's validated, you can set up Slack to query the bot by POSTing to the /ask endpoint as curl is doing above.

With some work, this could pull from a GDoc instead of a .docx and generate new embeddings on a schedule so that as the doc is updated, the bot will have updated answers.
