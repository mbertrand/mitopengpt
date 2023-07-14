import time
import psycopg2
import tiktoken
import re
import openai
import numpy as np
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
from psycopg2.extras import RealDictCursor

load_dotenv()

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

class PGChunk:
    def __init__(self, content_file, title, url, content, content_length, content_tokens, embedding):
        self.run_title = content_file["run_title"]
        self.run_id = content_file["run_id"]
        self.run_url = content_file["run_url"]
        self.page_title = title
        self.page_url = url
        self.content = content
        self.content_length = content_length
        self.content_tokens = content_tokens
        self.embedding = embedding

class PGPage:
    def __init__(self, title, url, content, length, tokens, chunks):
        self.title = title
        self.url = url
        self.content = content
        self.length = length
        self.tokens = tokens
        self.chunks = chunks

def get_title(content_file):
    return (content_file["content_title"] or content_file["title"] or content_file["key"].split('/')[-1])

def get_url(content_file):
    if content_file["key"]:
        return f'https://ocw.mit.edu/{content_file["key"]}'
    

def get_content(content_file):
    lines = [f"@@@^^^{line.strip()}" for line in re.sub(r"[^\s\w\.]+", "", content_file["content"]).split("\n") if line.strip() != ""]
    if len(lines) > 0:
        lines = ' '.join(lines)
        return lines
    else:
        return None


def chunk_file(content):
    CHUNK_SIZE = 200
    CHUNK_MAX = 250
    page_text_chunks = [];
    if num_tokens_from_string(content, "cl100k_base") > CHUNK_SIZE:
        split = '@@@^^^'.join(content.split('. ')).split('@@@^^^')
        chunkText = ""
        for sentence in split:
            sentence = sentence.strip()
            if len(sentence) == 0: 
                continue
            sentence_tokens = num_tokens_from_string(sentence, "cl100k_base");
            if sentence_tokens > CHUNK_SIZE:
                continue
            chunk_tokens = num_tokens_from_string(chunkText, "cl100k_base");
            if chunk_tokens + sentence_tokens > CHUNK_SIZE:
                page_text_chunks.append(chunkText.strip());
                chunkText = "";
            if re.search('[a-zA-Z]', sentence[-1]):
                chunkText += sentence + '. '
            else:
                chunkText += sentence + ' '
        page_text_chunks.append(chunkText.strip());
    else:
        page_text_chunks.append(content.strip())
    
    if len(page_text_chunks) > 2:
        last_elem = num_tokens_from_string(page_text_chunks[-1], "cl100k_base")
        second_to_last_elem = num_tokens_from_string(page_text_chunks[-2], "cl100k_base")
        if last_elem + second_to_last_elem < CHUNK_MAX:
            page_text_chunks[-2] += page_text_chunks[-1]
            page_text_chunks.pop()
    
    return page_text_chunks


def embed_chunk(resource, title, url, content):
    embedding = openai.Embedding.create(
        input = content, 
        model = 'text-embedding-ada-002')['data'][0]['embedding']
    chunk = PGChunk(resource, title, url, content, len(content), num_tokens_from_string(content, "cl100k_base"), embedding)
    return chunk

def make_file_embeddings(cur, content_file):
    title = get_title(content_file)
    content = get_content(content_file)
    url = get_url(content_file)
    if content == None:
        return
    page_text_chunks = chunk_file(content)

    for chunk in page_text_chunks:
        try:
            pg_chunk = embed_chunk(content_file, title, url, chunk)
        except:
            print("Embed API request failed, trying again in 5 seconds...")
            time.sleep(5)
            try:
                pg_chunk = embed_chunk(content_file, title, url, chunk)
            except Exception as e:
                print(f"Failed to embed {content_file['title']}")
                print(e)
                return        
        embedding = np.array(pg_chunk.embedding)
        sql = 'INSERT INTO ' + os.getenv('POSTGRES_TABLE_NAME') + '(run_title, run_id, run_url, page_title, page_url, content, content_length, content_tokens, embedding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);'
        cur.execute(sql, (
            pg_chunk.run_title,
            pg_chunk.run_id,
            pg_chunk.run_url,
            pg_chunk.page_title,
            pg_chunk.page_url,
            pg_chunk.content,
            str(pg_chunk.content_length),
            str(pg_chunk.content_tokens),
            embedding))
       

def main():
    openai.api_key = os.getenv('OPENAI_API_KEY')
    conn_open = None
    conn_vector = None

    try :
        print('Connecting to the Open database...')
        conn_open = psycopg2.connect(
            host = os.getenv('OPEN_POSTGRES_HOST'),
            database = os.getenv('OPEN_POSTGRES_DB_NAME'),
            user = os.getenv('OPEN_POSTGRES_USERNAME'),
            password = os.getenv('OPEN_POSTGRES_PASSWORD'),
            cursor_factory=RealDictCursor
        )

        cur_open = conn_open.cursor()
        start_course_id = os.getenv('START_COURSE_ID', "50f8d6059dd4313a5e46b05ba5365d2a+14.472")
        #courses/14-472-public-economics-ii-spring-2004

        print('Connecting to the vector PostgreSQL database...')
        conn_vector = psycopg2.connect(
            host = os.getenv('POSTGRES_HOST'),
            database = os.getenv('POSTGRES_DB_NAME'),
            user = os.getenv('POSTGRES_USERNAME'),
            password = os.getenv('POSTGRES_PASSWORD')
        )
        register_vector(conn_vector)

        OPEN_QUERY = """
        SELECT cf.id, cf.key, cf.title, cf.content, cf.content_title, cf.url, run.title as run_title, run.id as run_id, run.url as run_url, run.platform, course.course_id FROM course_catalog_contentfile as cf 
        LEFT JOIN course_catalog_learningresourcerun AS run ON cf.run_id = run.id INNER JOIN course_catalog_course AS course ON run.object_id = course.id
        WHERE cf.content IS NOT NULL and cf.content != '' and course.published IS TRUE and run.published IS TRUE and course.course_id >= %s ORDER BY course.course_id ASC, run.run_id ASC, cf.id ASC;
        """

        print("Getting content files...")
        cur_open.execute(OPEN_QUERY, [start_course_id,])
        content_files = cur_open.fetchall()

        print("Start embedding files...")
        course = None
        run = None
        for content_file in content_files:
            if not content_file["content"].strip():
                continue
            if content_file['course_id'] != course:
                print(f"Course: {content_file['course_id']}")
                course = content_file['course_id']
            if content_file['run_id'] != run:
                print(f"(Run: {content_file['run_id']})")
                run = content_file['run_id']
            print(f"Embedding {content_file['key']}")
            cur_vector = conn_vector.cursor()
            make_file_embeddings(cur_vector, content_file)
            print("Committing...")
            conn_vector.commit()
            cur_vector.close()
            

    except (Exception, psycopg2.DatabaseError) as error:
        raise error
    finally:
        if conn_vector is not None:
            conn_vector.close()
            print('Vector database connection closed.')
        if conn_open is not None:
            conn_open.close()
            print('MIT Open database connection closed.')           

if __name__ == "__main__":
    main()