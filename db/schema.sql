-- ============================================================
-- Mentor AN — Supabase Schema
-- Execute no Supabase SQL Editor (supabase.com → SQL Editor)
-- ============================================================

-- 1. Habilitar extensão pgvector
create extension if not exists vector;

-- 2. Tabela de chunks da base de conhecimento
create table if not exists chunks (
    id          uuid primary key default gen_random_uuid(),
    content     text        not null,
    embedding   vector(1536) not null,
    source      text,
    title       text,
    chunk_index integer,
    created_at  timestamptz default now()
);

-- Índice HNSW para busca vetorial rápida (melhor para produção)
create index if not exists chunks_embedding_idx
    on chunks using hnsw (embedding vector_cosine_ops)
    with (m = 16, ef_construction = 64);

-- 3. Função de busca semântica
create or replace function match_chunks(
    query_embedding vector(1536),
    match_count     int     default 5,
    min_score       float   default 0.65
)
returns table (
    id          uuid,
    content     text,
    source      text,
    title       text,
    score       float
)
language sql stable
as $$
    select
        id,
        content,
        source,
        title,
        1 - (embedding <=> query_embedding) as score
    from chunks
    where 1 - (embedding <=> query_embedding) >= min_score
    order by embedding <=> query_embedding
    limit match_count;
$$;

-- 4. Tabela de sessões (histórico de conversa por número)
create table if not exists sessions (
    id         bigserial   primary key,
    phone      text        not null,
    role       text        not null check (role in ('user', 'assistant')),
    content    text        not null,
    created_at timestamptz default now()
);

create index if not exists sessions_phone_idx
    on sessions (phone, created_at desc);

-- 5. Tabela de logs de conversa
create table if not exists conversation_logs (
    id           uuid primary key default gen_random_uuid(),
    phone_suffix text,
    question     text,
    sources      jsonb,
    had_fallback boolean,
    latency_ms   integer,
    created_at   timestamptz default now()
);
