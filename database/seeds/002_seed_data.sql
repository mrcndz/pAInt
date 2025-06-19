-- Seed data for pAInt catalog
-- Sample paint products based on Suvinil catalog

-- Insert sample users
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@paint.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeyFwtO4rZpgqB1Wa', 'admin'), -- password: admin123
('demo_user', 'demo@paint.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeyFwtO4rZpgqB1Wa', 'user'); -- password: demo123

-- Insert sample paint products (Suvinil-inspired catalog) with Portuguese features
INSERT INTO paint_products (name, color, surface_types, environment, finish_type, features, product_line, price) VALUES
-- Premium Line - Interior
('Suvinil Premium Branco Gelo', 'Branco Gelo', ARRAY['parede', 'teto'], 'internal', 'matte', ARRAY['lavável', 'antimofo', 'ecológico'], 'Premium', 89.90),
('Suvinil Premium Azul Serenidade', 'Azul Serenidade', ARRAY['parede'], 'internal', 'satin', ARRAY['lavável', 'resistente a manchas'], 'Premium', 94.90),
('Suvinil Premium Cinza Concreto', 'Cinza Concreto', ARRAY['parede'], 'internal', 'matte', ARRAY['lavável', 'visual moderno'], 'Premium', 92.90),
('Suvinil Premium Verde Natureza', 'Verde Natureza', ARRAY['parede'], 'internal', 'satin', ARRAY['lavável', 'tranquilizante'], 'Premium', 91.90),
('Suvinil Premium Rosa Delicado', 'Rosa Delicado', ARRAY['parede'], 'internal', 'matte', ARRAY['lavável', 'tom suave'], 'Premium', 89.90),

-- Premium Line - Exterior
('Suvinil Premium Fachada Branco', 'Branco', ARRAY['parede', 'fachada'], 'external', 'semi-gloss', ARRAY['resistente ao tempo', 'antimofo', 'proteção UV'], 'Premium', 124.90),
('Suvinil Premium Fachada Terracota', 'Terracota', ARRAY['parede', 'fachada'], 'external', 'semi-gloss', ARRAY['resistente ao tempo', 'não desbota'], 'Premium', 129.90),

-- Standard Line - Interior
('Suvinil Standard Branco Neve', 'Branco Neve', ARRAY['parede', 'teto'], 'internal', 'matte', ARRAY['lavável'], 'Standard', 59.90),
('Suvinil Standard Amarelo Suave', 'Amarelo Suave', ARRAY['parede'], 'internal', 'matte', ARRAY['lavável', 'alegre'], 'Standard', 62.90),
('Suvinil Standard Azul Céu', 'Azul Céu', ARRAY['parede'], 'internal', 'satin', ARRAY['lavável'], 'Standard', 64.90),
('Suvinil Standard Vermelho Paixão', 'Vermelho Paixão', ARRAY['parede'], 'internal', 'satin', ARRAY['lavável', 'vibrante'], 'Standard', 66.90),
('Suvinil Standard Marrom Chocolate', 'Marrom Chocolate', ARRAY['parede'], 'internal', 'matte', ARRAY['lavável', 'aconchegante'], 'Standard', 63.90),

-- Specialty Products
('Suvinil Esmalte Branco', 'Branco', ARRAY['madeira', 'metal'], 'both', 'gloss', ARRAY['durável', 'secagem rápida'], 'Specialty', 79.90),
('Suvinil Esmalte Preto', 'Preto', ARRAY['madeira', 'metal'], 'both', 'gloss', ARRAY['durável', 'elegante'], 'Specialty', 79.90),
('Suvinil Piso Cinza Chumbo', 'Cinza Chumbo', ARRAY['piso'], 'both', 'semi-gloss', ARRAY['alto tráfego', 'antiderrapante'], 'Specialty', 94.90),

-- Economy Line
('Suvinil Econômica Branco', 'Branco', ARRAY['parede', 'teto'], 'internal', 'matte', ARRAY['cobertura básica'], 'Economy', 39.90),
('Suvinil Econômica Creme', 'Creme', ARRAY['parede'], 'internal', 'matte', ARRAY['cobertura básica'], 'Economy', 41.90),
('Suvinil Econômica Azul Claro', 'Azul Claro', ARRAY['parede'], 'internal', 'matte', ARRAY['cobertura básica'], 'Economy', 42.90);

-- Note: AI-enriched fields (ai_summary, usage_tags) will be populated by the AI service
-- during the data enrichment process (Epic 4)