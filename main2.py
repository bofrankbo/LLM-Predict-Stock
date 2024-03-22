import os
from multiprocessing import Pool
from langchain_google_genai import ChatGoogleGenerativeAI

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCPJgPIo1rhfmt2lRkrdMLUQQdUIEhWjys"

prompt = ["Write a limerick about LLMs.", "Write a story about School."]
llm = ChatGoogleGenerativeAI(model="gemini-pro")


def f(i):
    print("wrwe")
    response = llm.invoke(prompt[i])
    print("prompt: " + prompt[i])
    print("response: " + response.content)
    print("_" * 80)


if __name__ == '__main__':

    with Pool(5) as p:
        p.map(f, [0, 1])
