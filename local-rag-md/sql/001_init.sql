CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id BIGSERIAL PRIMARY KEY,
  path TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  file_hash TEXT NOT NULL,
  file_size_bytes BIGINT NOT NULL,
  modified_at TIMESTAMPTZ NOT NULL,
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
  id BIGSERIAL PRIMARY KEY,
  document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  heading TEXT,
  content TEXT NOT NULL,
  token_estimate INTEGER NOT NULL,
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  embedding VECTOR(768) NOT NULL,
  tsv TSVECTOR GENERATED ALWAYS AS (
    to_tsvector('simple', COALESCE(heading, '') || ' ' || content)
  ) STORED,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_documents_modified_at ON documents (modified_at DESC);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_tsv ON chunks USING GIN (tsv);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw ON chunks USING HNSW (embedding vector_cosine_ops);

