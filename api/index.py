import os
import json
from typing import List
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from .utils.prompt import ClientMessage, convert_to_openai_messages
from .utils.tools import get_current_weather
import vertexai
from google import auth as google_auth
from google.auth.transport import requests as google_requests
import requests
import logging
from fastapi.encoders import jsonable_encoder



load_dotenv(".env.local")
logger = logging.getLogger(__name__)

app = FastAPI()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

projectId = os.environ.get("GOOGLE_PROJECT_ID")
location = 'us-central1'
resourceId = '5929349549247168512'

vertexai.init(project=projectId, location=location)


class Request(BaseModel):
    messages: List[ClientMessage]


available_tools = {
    "get_current_weather": get_current_weather,
}

def do_stream(messages: List[ChatCompletionMessageParam]):
    stream = client.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        stream=True,
        tools=[{
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather at a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "The latitude of the location",
                        },
                        "longitude": {
                            "type": "number",
                            "description": "The longitude of the location",
                        },
                    },
                    "required": ["latitude", "longitude"],
                },
            },
        }]
    )

    return stream

def stream_text(messages: List[ChatCompletionMessageParam], protocol: str = 'data'):
    draft_tool_calls = []
    draft_tool_calls_index = -1

    stream = client.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        stream=True,
        tools=[{
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather at a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "The latitude of the location",
                        },
                        "longitude": {
                            "type": "number",
                            "description": "The longitude of the location",
                        },
                    },
                    "required": ["latitude", "longitude"],
                },
            },
        }]
    )

    for chunk in stream:
        for choice in chunk.choices:
            if choice.finish_reason == "stop":
                continue

            elif choice.finish_reason == "tool_calls":
                for tool_call in draft_tool_calls:
                    yield '9:{{"toolCallId":"{id}","toolName":"{name}","args":{args}}}\n'.format(
                        id=tool_call["id"],
                        name=tool_call["name"],
                        args=tool_call["arguments"])

                for tool_call in draft_tool_calls:
                    tool_result = available_tools[tool_call["name"]](
                        **json.loads(tool_call["arguments"]))

                    yield 'a:{{"toolCallId":"{id}","toolName":"{name}","args":{args},"result":{result}}}\n'.format(
                        id=tool_call["id"],
                        name=tool_call["name"],
                        args=tool_call["arguments"],
                        result=json.dumps(tool_result))

            elif choice.delta.tool_calls:
                for tool_call in choice.delta.tool_calls:
                    id = tool_call.id
                    name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    if (id is not None):
                        draft_tool_calls_index += 1
                        draft_tool_calls.append(
                            {"id": id, "name": name, "arguments": ""})

                    else:
                        draft_tool_calls[draft_tool_calls_index]["arguments"] += arguments

            else:
                yield '0:{text}\n'.format(text=json.dumps(choice.delta.content))

        if chunk.choices == []:
            usage = chunk.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens

            yield 'e:{{"finishReason":"{reason}","usage":{{"promptTokens":{prompt},"completionTokens":{completion}}},"isContinued":false}}\n'.format(
                reason="tool-calls" if len(
                    draft_tool_calls) > 0 else "stop",
                prompt=prompt_tokens,
                completion=completion_tokens
            )

def get_identity_token():
    credentials, _ = google_auth.default()
    auth_request = google_requests.Request()
    credentials.refresh(auth_request)
    return credentials.token


# @app.post("/api/chat")
# async def handle_chat_data(request: Request, protocol: str = Query('data')):
#     messages = request.messages
#     openai_messages = convert_to_openai_messages(messages)

#     # response = StreamingResponse(stream_text(openai_messages, protocol))
#     # response.headers['x-vercel-ai-data-stream'] = 'v1'
#     # return response
#     response = requests.post(
#         f"https://{location}-aiplatform.googleapis.com/v1/projects/{projectId}/locations/{location}/reasoningEngines/{resourceId}:streamQuery",
#         headers={
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {get_identity_token()}",
#         },
#         data=json.dumps({
#             "class_method": "stream_query",
#             "input": {
#                 "input": {"messages": openai_messages},
#             },
#         }),
#         stream=True,
#     )
#     response.headers['x-vercel-ai-data-stream'] = 'v1'
#     return response

@app.post("/api/chat")
async def handle_chat_data(request: Request, protocol: str = Query('data')):
    # Convert request data to dict first
    messages = request.messages
    openai_messages = convert_to_openai_messages(messages)
    print(f"messages", messages)
    print(f"openai_messages", openai_messages)
    try:
        # Create the payload as a plain dict
        payload = {
            "class_method": "stream_query",
            "input": {
                "message": "What is the exchange rate from US dollars to Swedish currency?",
                "user_id": "YOUR_USER_ID"
                # "messages": [  # Optional: if you still want to include conversation history
                #     {
                #         "role": "user",
                #         "content": "What is the exchange rate from US dollars to Swedish currency?"
                #     }
                # ]
            }
        }

        logger.debug(f"Sending payload: {json.dumps(payload, indent=2)}")

        return requests.post(
            f"https://{location}-aiplatform.googleapis.com/v1/projects/{projectId}/locations/{location}/reasoningEngines/{resourceId}:streamQuery",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {get_identity_token()}",
            },
            data=json.dumps(payload),
            stream=True,
        )

        logger.info(f"Response status: {response.status_code}")

        # Create a streaming response
        async def generate():
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk

        return StreamingResponse(
            generate(),
            media_type="application/json",
            headers={'x-vercel-ai-data-stream': 'v1'}
        )

    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))