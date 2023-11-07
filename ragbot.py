from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import pandas as pd
import openai
from scipy import spatial
import pandas as pd
from openai import OpenAI
import ast
import os
from typing import List

app = FastAPI()

SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET')


EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"
embeddings_path = "embeddings.csv"  # Eventually should point to something we can update dynamically

# Rank strings from the doc to the user's query by relatedness
def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 5
) -> tuple[List[str], List[float]]:
    
    # Generate the query embedding
    query_embedding_response = openai.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, ast.literal_eval(row["embedding"])))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

# Read the embeddings from the CSV file
df = pd.read_csv(embeddings_path)

# Generate a query message for GPT
def query_message(
    query: str,
    df: pd.DataFrame,
    model: str = GPT_MODEL,
) -> str:
    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = 'Use the below sections from the company\'s Security Whitepaper to answer subsequent questions. If the answer cannot be found, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction + question
    for string in strings:
        next_article = f'\n\nWhitepaper section:\n"""\n{string}\n"""'
        message += next_article
    message += f'\n\nBased on the above, can you answer {query}?'
    return message

def ask(
    query: str,
    df: pd.DataFrame = df,
    model: str = GPT_MODEL,
    print_message: bool = False,
) -> str:
    message = query_message(query, df, model=model)
    client = OpenAI()
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": "You answer questions about the company's security program."},
            {"role": "user", "content": message}
            ],
        temperature=0
    )

    if print_message:
        print(message)


    response_message = response.choices[0].message.content
    return response_message

@app.post('/ask')
async def ask_endpoint(request: Request):  
    try:
        body = await request.json()  
        query = body['query']
        response = ask(query)  
        return JSONResponse({"response": response})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4433)