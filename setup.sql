--  RUN 1st
-- create extension vector;

-- RUN 2nd
create table mit_open_chunks (
    page_title text,
    page_url text,
    run_title text,
    run_id bigint,
    run_url text,
    content text,
    content_length bigint,
    content_tokens bigint,
    embedding vector (1536)
);


-- RUN 3rd after running the scripts
create or replace function mit_open_gpt_search (
    query_embedding vector (1536),
    similarity_threshold float,
    match_count int
)
returns table (
    page_title text,
    page_url text,
    content text,
    content_length bigint,
    content_tokens bigint,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        mit_open_chunks.page_title,
        mit_open_chunks.page_url,
        mit_open_chunks.content,
        mit_open_chunks.content_length,
        mit_open_chunks.content_tokens,        
        1 - (mit_open_chunks.embedding <=> query_embedding) as similarity
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