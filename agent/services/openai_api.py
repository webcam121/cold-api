from openai import OpenAI
import os
import dotenv

dotenv.load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_KEY"),
)


def generate(messages, temperature, model, max_tokens, stream=False):
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return completion.choices[0].message.content
