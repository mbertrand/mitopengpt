# MIT OpenCourseware GPT

AI-powered search and chat for [MIT OpenCourseware](https://open.mit.edu/).

## How It Works

MIT OpenCourseware GPT provides 2 things:

1. A search interface.
2. A chat interface.

### Search

Search was created with [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings) (`text-embedding-ada-002`).

First, we loop over the documentation urls and generate embeddings for each chunk of text in the page.

Then in the app we take the user's search query, generate an embedding, and use the result to find the pages that contain similar content

The comparison is done using cosine similarity across our database of vectors.

Results are then ranked by similarity score and returned to the user.

### Chat

Chat builds on top of search. It uses search results to create a prompt that is fed into GPT-3.5-turbo.

This allows for a chat-like experience where the user can ask questions about AWS documentation and get answers.

## Running Locally

Here's a quick overview of how to run it locally.

### Requirements

1. Set up OpenAI

You'll need an OpenAI API key to generate embeddings (locally).

2. Set up a local image of PostgreSQL (I recommend the pgvector docker image)

There is a setup.sql file in the root of the repo that you can use to set up the database.

Run that in a SQL editor.

Note: Or, connect to any PostgreSQL server using the env variables defined below

### Repo Setup

3. Clone repo

```bash
git clone https://github.com/mitodl/semantic-mitopen.git
```

4. Set up environment variables

Create a .env file in the root of the repo folder with the following variables:

```bash
OPENAI_API_KEY = # Your OpenAI API key
# Connection info for the Postgres database that will store text chunks and embeddings
POSTGRES_HOST =
POSTGRES_DB_NAME =
POSTGRES_USERNAME =
POSTGRES_TABLE_NAME = #if you used setup.sql, this should be "mit_open_chunks"
POSTGRES_SEARCH_FUNCTION = #if you used setup.sql, this should be "mit_open_gpt_search"
POSTGRES_PASSWORD =
# Connection info for the Postgres database from which MIT Open content will be retrieved
OPEN_POSTGRES_HOST=
OPEN_POSTGRES_DB_NAME=
OPEN_POSTGRES_USERNAME=
OPEN_POSTGRES_PASSWORD=
```

### Dataset

5. Run parsing script

```bash
docker-compose run --rm web python3 data/ocw-upload.py
```


### App

7. Run entire app

```bash
docker-compose up
```

## Credits

Thanks to [Alex Sima](https://github.com/alexy201/awsdocsgpt) who developed the project on which this is heavily based.
