import logging
import os

import numpy as np
import openai
from fastapi import APIRouter, Request

import semantic_mitopen.exceptions as exceptions
from semantic_mitopen.schemas import chat_response, message, query, search_response

router = APIRouter()
_logger = logging.getLogger(__name__)


@router.post(
    "/chat",
    response_model=chat_response,
    summary="Get response from OpenAI Chat Completion with prompt string and result count",
    response_description="Answer (string which represents the completion) and sources used",
)
async def chat_handler(request: Request, query: query):
    _logger.info({"message": "Calling Chat Endpoint"})
    rows = await helper(request, query)

    pages = []
    sources = ""
    for row in rows:
        dic = dict(row)
        pages.append(dic)
        sources += "SOURCE TITLE: " + dic["content_title"] + "\n"
        sources += "SOURCE CONTENT: " + dic["content"]
    prompt_context = f"""
    Answer the question based on the context below, and if the question can't be answered based on the context,
    say \"Sorry, I can't find an answer from the MIT course content\"\n\n
    PLEASE MAKE THE RESPONSE A {query.sentences.upper()} {query.sentences.upper()} {query.sentences.upper()} LENGTH THIS IS VERY IMPORTANT!!!
    If you are giving a SHORT or MEDIUM response, do not add a long response with [Answer] or an "Answer" heading.
    Context: {sources}\n\n---\n\nQuestion: {query.prompt}\nAnswer:
    """

    messages = []
    messages.append(
        message(
            role="system",
            content=f"""You are a helpful and knowledgeable MIT professor that helps students with their questions about MIT courses.
                       In your responses, when you want to include a header, include it like: # [your header].
                       when you want to include a sub-header, include it like: ## [your subs-header].
                       when you want to include a piece of code, include it like: ```[your entire code bit]```.
                       MAKE SURE TO FORMAT ALL CODE CORRECTLY!!! INCLUDE PROPER INDENTING AND SPACING!!!
                       For bold text, just render it like **bold text**. Render ordered/unordered lists in Markdown.
                       For links, render as [link title](https://www.example.com).
                       Essentially just give your entire response as a Markdown document.""",
        )
    )
    messages.append(message(role="user", content=prompt_context))

    return chat_response(messages=messages, sources=pages)


@router.post(
    "/search",
    response_model=search_response,
    summary="Get chunks from Postgres DB with prompt string and result count",
    response_description="Sources that match the prompt (in a list)",
)
async def search_handler(request: Request, query: query):
    _logger.info({"message": "Calling Search Endpoint"})
    rows = await helper(request, query)
    response = []
    for row in rows:
        response.append(dict(row))

    return search_response(sources=response)


async def helper(request: Request, query: query):
    try:
        _logger.info({"message": "Creating embedding"})
        _logger.info({"api_key": query.api_key})
        embedding = openai.Embedding.create(
            api_key=query.api_key, input=query.prompt, model="text-embedding-ada-002"
        )["data"][0]["embedding"]
        sql = "SELECT * FROM " + os.getenv("POSTGRES_SEARCH_FUNCTION") + "($1, $2, $3)"
    except:
        _logger.error({"message": "Issue with creating an embedding."})
        raise exceptions.InvalidPromptEmbeddingException

    try:
        _logger.info({"message": "Querying Postgres"})
        res = await request.app.state.db.fetch_rows(
            sql, np.array(embedding), query.similarity_threshold, query.results
        )
    except Exception as e:
        _logger.error({"message": "Issue with querying Postgres." + str(e)})
        raise exceptions.InvalidPostgresQueryException

    return res
