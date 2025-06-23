CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS paint_products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    color VARCHAR(100) NOT NULL,
    surface_types TEXT[] NOT NULL DEFAULT '{}', -- ['madeira', 'metal', 'parede', 'teto']
    environment VARCHAR(50) NOT NULL CHECK (environment IN ('interno', 'externo', 'ambos')),
    finish_type VARCHAR(50) NOT NULL, -- 'fosco', 'acetinado', 'semi-brilho', 'brilhante'
    features TEXT[] DEFAULT '{}', -- ['lavável', 'antimofo', 'secagem rápida', 'ecológico']
    product_line VARCHAR(100) NOT NULL, -- 'Premium', 'Padrão', 'Econômico', 'Especial'
    price DECIMAL(10,2),
    ai_summary TEXT, -- Enriquecido por IA (AI-generated)
    usage_tags TEXT[] DEFAULT '{}', -- ['family-friendly', 'modern-look', 'high-traffic']
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_uuid UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_data JSONB DEFAULT '{}',
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_paint_color ON paint_products(color);
CREATE INDEX IF NOT EXISTS idx_paint_environment ON paint_products(environment);
CREATE INDEX IF NOT EXISTS idx_paint_finish ON paint_products(finish_type);
CREATE INDEX IF NOT EXISTS idx_paint_product_line ON paint_products(product_line);

CREATE INDEX IF NOT EXISTS idx_paint_surface_types ON paint_products USING GIN(surface_types);
CREATE INDEX IF NOT EXISTS idx_paint_features ON paint_products USING GIN(features);
CREATE INDEX IF NOT EXISTS idx_paint_usage_tags ON paint_products USING GIN(usage_tags);

CREATE INDEX IF NOT EXISTS idx_paint_text_search ON paint_products USING GIN(
    to_tsvector('portuguese', COALESCE(name, '') || ' ' || COALESCE(ai_summary, ''))
);

CREATE INDEX IF NOT EXISTS paint_products_embedding_idx ON paint_products 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_activity ON chat_sessions(last_activity);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_uuid ON chat_sessions(session_uuid);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_paint_products_updated_at ON paint_products;
CREATE TRIGGER update_paint_products_updated_at 
    BEFORE UPDATE ON paint_products 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_chat_sessions_updated_at ON chat_sessions;
CREATE TRIGGER update_chat_sessions_updated_at 
    BEFORE UPDATE ON chat_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
