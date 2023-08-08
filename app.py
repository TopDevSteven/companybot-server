from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai
import re
import os
import ast
import sqlite3
from sqlite3 import Error




load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

message = []
name = ""
messages = [ {"role": "system", "content": 
            "You are a intelligent assistant."} ]
coulmns = []

@app.post("/user/")
async def user(reqeust: Request):
    body = await reqeust.json()
    name = body['username']
    index = 0
    conn = None
    try:
        conn = sqlite3.connect(r"product.db")
    except Error as e:
        print(e)

    cur = conn.cursor()
    table_name = 'product'

    # Execute a query to get column names
    query = f"PRAGMA table_info({table_name})"
    cur.execute(query)

    # Fetch the column names
    coulmns = [row[1] for row in cur.fetchall()]
    # print(coulmns)
    cur.execute("SELECT * FROM product WHERE `First Name` = ?", (name,))
    rows = cur.fetchall()
    data_str = "This is my data\n"

    if len(rows) > 0:
        for i in range(len(rows[0])):
            data_str += coulmns[i] + " : " + str(rows[0][i]) + "\n"
        # print(data_str)
        data_str += """Please provide flexible and readable answer based on above data.\n"""
        # data_str += "Though what question is, must output Yes\n The question is: what is lot number"
        # print(data_str)
        messages.append(
                {"role": "user", "content": data_str},
            )
        
        return {"reply" : "valid"}
    else: return {"reply" : "failed"}


@app.post("/chat/")
async def chat(reqeust: Request):
    body = await reqeust.json()


    message = body['usemsg']
    if not message:
        print("wrong")
    prompt = """ Output date must be the follwing format. "7th Aug 2023"
    You have to answer like these:
    firstly you have to mention the thx and agree for the question with several methods and styles.
    secondly you have to answer the questions. in the case of the date result, you have to consider the past(was or were) , future (will) and recent based on current time. for instance, in the case of "the site cut date is 8th June 2022." it is 'was', not 'is'.
    finally you have to mention the recommend information or question.

    you have to summarize above steps like human.

"""
    prompt += message
    print(prompt)
    if message:
        messages.append(
            {"role": "user", "content": prompt},
        )
        print(messages)
        chat = openai.ChatCompletion.create(
            model="gpt-4", messages=messages
        )
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})
    return {"message": reply}
