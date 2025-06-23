-- Seed data for pAInt catalog
-- Sample paint products based on Suvinil catalog

-- Insert sample users
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@paint.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeyFwtO4rZpgqB1Wa', 'admin'), -- password: admin123
('demo_user', 'demo@paint.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeyFwtO4rZpgqB1Wa', 'user'); -- password: demo123

-- Insert sample paint products (Suvinil-inspired catalog) with Portuguese features
INSERT INTO paint_products (name, color, surface_types, environment, finish_type, features, product_line, price) VALUES
-- Premium Line - Interior
('Suvinil Premium Branco Gelo', 'Branco Gelo', ARRAY['parede', 'teto'], 'interno', 'fosco', ARRAY['lavável', 'antimofo', 'ecológico'], 'Premium', 89.90),
('Suvinil Premium Azul Serenidade', 'Azul Serenidade', ARRAY['parede'], 'interno', 'acetinado', ARRAY['lavável', 'resistente a manchas'], 'Premium', 94.90),
('Suvinil Premium Cinza Concreto', 'Cinza Concreto', ARRAY['parede'], 'interno', 'fosco', ARRAY['lavável', 'visual moderno'], 'Premium', 92.90),
('Suvinil Premium Verde Natureza', 'Verde Natureza', ARRAY['parede'], 'interno', 'acetinado', ARRAY['lavável', 'tranquilizante'], 'Premium', 91.90),
('Suvinil Premium Rosa Delicado', 'Rosa Delicado', ARRAY['parede'], 'interno', 'fosco', ARRAY['lavável', 'tom suave'], 'Premium', 89.90),

-- Premium Line - Exterior
('Suvinil Premium Fachada Branco', 'Branco', ARRAY['parede', 'fachada'], 'externo', 'semi-brilho', ARRAY['resistente ao tempo', 'antimofo', 'proteção UV'], 'Premium', 124.90),
('Suvinil Premium Fachada Terracota', 'Terracota', ARRAY['parede', 'fachada'], 'externo', 'semi-brilho', ARRAY['resistente ao tempo', 'não desbota'], 'Premium', 129.90),

-- Standard Line - Interior
('Suvinil Standard Branco Neve', 'Branco Neve', ARRAY['parede', 'teto'], 'interno', 'fosco', ARRAY['lavável'], 'Padrão', 59.90),
('Suvinil Standard Amarelo Suave', 'Amarelo Suave', ARRAY['parede'], 'interno', 'fosco', ARRAY['lavável', 'alegre'], 'Padrão', 62.90),
('Suvinil Standard Azul Céu', 'Azul Céu', ARRAY['parede'], 'interno', 'acetinado', ARRAY['lavável'], 'Padrão', 64.90),
('Suvinil Standard Vermelho Paixão', 'Vermelho Paixão', ARRAY['parede'], 'interno', 'acetinado', ARRAY['lavável', 'vibrante'], 'Padrão', 66.90),
('Suvinil Standard Marrom Chocolate', 'Marrom Chocolate', ARRAY['parede'], 'interno', 'fosco', ARRAY['lavável', 'aconchegante'], 'Padrão', 63.90),

-- Specialty Products
('Suvinil Esmalte Branco', 'Branco', ARRAY['madeira', 'metal'], 'ambos', 'brilhante', ARRAY['durável', 'secagem rápida'], 'Especial', 79.90),
('Suvinil Esmalte Preto', 'Preto', ARRAY['madeira', 'metal'], 'ambos', 'brilhante', ARRAY['durável', 'elegante'], 'Especial', 79.90),
('Suvinil Piso Cinza Chumbo', 'Cinza Chumbo', ARRAY['piso'], 'ambos', 'semi-brilho', ARRAY['alto tráfego', 'antiderrapante'], 'Especial', 94.90),

-- Economy Line
('Suvinil Econômica Branco', 'Branco', ARRAY['parede', 'teto'], 'interno', 'fosco', ARRAY['cobertura básica'], 'Econômico', 39.90),
('Suvinil Econômica Creme', 'Creme', ARRAY['parede'], 'interno', 'fosco', ARRAY['cobertura básica'], 'Econômico', 41.90),
('Suvinil Econômica Azul Claro', 'Azul Claro', ARRAY['parede'], 'interno', 'fosco', ARRAY['cobertura básica'], 'Econômico', 42.90);
