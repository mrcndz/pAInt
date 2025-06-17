-- Seed data for pAInt catalog
-- Sample paint products based on Suvinil catalog

-- Insert sample users
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@paint.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeyFwtO4rZpgqB1Wa', 'admin'), -- password: admin123
('demo_user', 'demo@paint.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeyFwtO4rZpgqB1Wa', 'user'); -- password: demo123

-- Insert sample paint products (Suvinil-inspired catalog)
INSERT INTO paint_products (name, color, surface_types, environment, finish_type, features, product_line, price) VALUES
-- Premium Line - Interior
('Suvinil Premium Branco Gelo', 'Branco Gelo', ARRAY['wall', 'ceiling'], 'internal', 'matte', ARRAY['washable', 'anti-mold', 'eco-friendly'], 'Premium', 89.90),
('Suvinil Premium Azul Serenidade', 'Azul Serenidade', ARRAY['wall'], 'internal', 'satin', ARRAY['washable', 'stain-resistant'], 'Premium', 94.90),
('Suvinil Premium Cinza Concreto', 'Cinza Concreto', ARRAY['wall'], 'internal', 'matte', ARRAY['washable', 'modern-look'], 'Premium', 92.90),
('Suvinil Premium Verde Natureza', 'Verde Natureza', ARRAY['wall'], 'internal', 'satin', ARRAY['washable', 'calming'], 'Premium', 91.90),
('Suvinil Premium Rosa Delicado', 'Rosa Delicado', ARRAY['wall'], 'internal', 'matte', ARRAY['washable', 'soft-tone'], 'Premium', 89.90),

-- Premium Line - Exterior
('Suvinil Premium Fachada Branco', 'Branco', ARRAY['wall', 'facade'], 'external', 'semi-gloss', ARRAY['weather-resistant', 'anti-mold', 'UV-protection'], 'Premium', 124.90),
('Suvinil Premium Fachada Terracota', 'Terracota', ARRAY['wall', 'facade'], 'external', 'semi-gloss', ARRAY['weather-resistant', 'fade-resistant'], 'Premium', 129.90),

-- Standard Line - Interior
('Suvinil Standard Branco Neve', 'Branco Neve', ARRAY['wall', 'ceiling'], 'internal', 'matte', ARRAY['washable'], 'Standard', 59.90),
('Suvinil Standard Amarelo Suave', 'Amarelo Suave', ARRAY['wall'], 'internal', 'matte', ARRAY['washable', 'cheerful'], 'Standard', 62.90),
('Suvinil Standard Azul Céu', 'Azul Céu', ARRAY['wall'], 'internal', 'satin', ARRAY['washable'], 'Standard', 64.90),
('Suvinil Standard Vermelho Paixão', 'Vermelho Paixão', ARRAY['wall'], 'internal', 'satin', ARRAY['washable', 'bold'], 'Standard', 66.90),
('Suvinil Standard Marrom Chocolate', 'Marrom Chocolate', ARRAY['wall'], 'internal', 'matte', ARRAY['washable', 'cozy'], 'Standard', 63.90),

-- Specialty Products
('Suvinil Esmalte Branco', 'Branco', ARRAY['wood', 'metal'], 'both', 'gloss', ARRAY['durable', 'quick-dry'], 'Specialty', 79.90),
('Suvinil Esmalte Preto', 'Preto', ARRAY['wood', 'metal'], 'both', 'gloss', ARRAY['durable', 'elegant'], 'Specialty', 79.90),
('Suvinil Piso Cinza Chumbo', 'Cinza Chumbo', ARRAY['floor'], 'both', 'semi-gloss', ARRAY['high-traffic', 'slip-resistant'], 'Specialty', 94.90),

-- Economy Line
('Suvinil Econômica Branco', 'Branco', ARRAY['wall', 'ceiling'], 'internal', 'matte', ARRAY['basic-coverage'], 'Economy', 39.90),
('Suvinil Econômica Creme', 'Creme', ARRAY['wall'], 'internal', 'matte', ARRAY['basic-coverage'], 'Economy', 41.90),
('Suvinil Econômica Azul Claro', 'Azul Claro', ARRAY['wall'], 'internal', 'matte', ARRAY['basic-coverage'], 'Economy', 42.90);

-- Note: AI-enriched fields (ai_summary, usage_tags) will be populated by the AI service
-- during the data enrichment process (Epic 4)