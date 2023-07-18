--  RUN 1st
create extension if not exists vector;

-- RUN 2nd
create table mit_open_chunks (
    run_title text,
    run_id bigint,
    run_key text,
    run_url text,
    platform varchar(10),
    content_id bigint,
    content_title text,
    content_url text,
    page_title text,
    page_url text,
    content text,
    content_hash varchar(32),
    content_length bigint,
    content_tokens bigint,
    embedding vector (1536),
    UNIQUE (platform, run_key, content_id, content_hash)
);


alter TABLE table_name ADD CONSTRAINT constraint_name UNIQUE (integer_column, boolean_column);

-- RUN 3rd after running the scripts
create or replace function mit_open_gpt_search (
    query_embedding vector (1536),
    similarity_threshold float,
    match_count int
)
returns table (
    content_title text,
    content_url text,
    content text,
    content_hash varchar(32),
    content_length bigint,
    content_tokens bigint,
    similarity float,
    run_url text,
    run_title text,
    run_key text
)
language plpgsql
as $$
begin
    return query
    select
        mit_open_chunks.content_title,
        mit_open_chunks.content_url,
        mit_open_chunks.content,
        mit_open_chunks.content_length,
        mit_open_chunks.content_tokens,
        1 - (mit_open_chunks.embedding <=> query_embedding) as similarity
        mit_open_chunks.run_url,
        mit_open_chunks.run_title
from mit_open_chunks
where 1 - (mit_open_chunks.embedding <=> query_embedding) > similarity_threshold
order by mit_open_chunks.embedding <=> query_embedding
limit match_count;
end;
$$;

-- RUN 4th
create index on mit_open_chunks
using ivfflat (embedding vector_cosine_ops)
with (lists = 100);
