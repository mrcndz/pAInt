# pAInt API - Postman Collection

Esta coleção do Postman contém todos os endpoints para testar o sistema de recomendação de tintas pAInt.

## 📁 Arquivos

- `pAInt_API_Collection.json` - Coleção principal com todos os endpoints
- `pAInt_Local_Environment.json` - Ambiente para desenvolvimento local
- `README.md` - Este guia de uso

## 🚀 Como Importar no Postman

### 1. Importar a Coleção
1. Abra o Postman
2. Clique em **Import** (botão no canto superior esquerdo)
3. Selecione o arquivo `pAInt_API_Collection.json`
4. Clique em **Import**

### 2. Importar o Ambiente
1. Clique em **Import** novamente
2. Selecione o arquivo `pAInt_Local_Environment.json`
3. Clique em **Import**
4. No canto superior direito, selecione o ambiente **"pAInt - Local Development"**

## 📋 Como Usar

### 1. **Primeiro: Fazer Login**
- Execute a requisição `Authentication > Login - Admin User`
- O token JWT será automaticamente salvo nas variáveis da coleção
- Todas as outras requisições usarão este token automaticamente

### 2. **Testar Recomendações**
Execute na ordem:
1. `AI Recommendations > New Conversation - Bedroom Paint`
2. `AI Recommendations > Follow-up - Premium Option Details`

Isso testará a persistência da conversa.

### 3. **Testar Múltiplas Sessões**
- Execute `Kitchen Paint Request` (cria nova sessão)
- Execute `External Paint Request` (cria outra sessão)
- Cada uma terá contexto separado

## 📊 Grupos de Testes

### 🔐 **Authentication**
- Login e validação de token
- **Executar primeiro** para autenticar todas as outras requisições

### 🤖 **AI Recommendations**
- Conversas com IA para recomendação de tintas
- Testa persistência de conversação
- Múltiplos cenários (quarto, cozinha, área externa)

### 💬 **Session Management**
- Gerenciamento de sessões de conversa
- Reset de sessões
- Listagem de sessões do usuário

### 🔍 **Direct Search & Filter**
- Busca direta sem IA (mais rápida)
- Filtros por critérios específicos

### 🏥 **System Health**
- Verificação de saúde dos serviços
- Não requer autenticação

### 🧪 **Conversation Persistence Tests**
- Testes específicos para validar persistência
- Execute sequencialmente para testar memória

## 🎯 Fluxo de Teste Recomendado

### **Teste Básico:**
1. `Authentication > Login - Admin User`
2. `AI Recommendations > New Conversation - Bedroom Paint`
3. `AI Recommendations > Follow-up - Premium Option Details`

### **Teste de Persistência:**
1. Execute o **Teste Básico**
2. Reinicie o serviço AI (`docker-compose restart ai-service`)
3. Execute novamente o `Follow-up` - deve lembrar do contexto

### **Teste de Múltiplas Sessões:**
1. `AI Recommendations > New Conversation - Bedroom Paint`
2. `AI Recommendations > Kitchen Paint Request`
3. Verifique que cada sessão tem contexto diferente

### **Teste Completo de Persistência:**
Execute sequencialmente:
1. `Conversation Persistence Tests > Test 1: Create Session`
2. `Conversation Persistence Tests > Test 2: Continue Conversation`
3. `Conversation Persistence Tests > Test 3: Reference Previous Context`

## 🔧 Variáveis Importantes

### **Automáticas (salvas automaticamente):**
- `access_token` - Token JWT após login
- `session_uuid` - UUID da sessão atual
- `user_id` - ID do usuário logado

### **Configuráveis:**
- `api_base_url` - URL do serviço API (padrão: localhost:8000)
- `ai_base_url` - URL do serviço AI (padrão: localhost:8001)

## 📝 Exemplos de Mensagens para Testar

### **Básicas:**
- "Preciso de tinta para meu quarto"
- "Quero uma cor azul para a sala"
- "Que tinta usar na cozinha?"

### **Específicas:**
- "Preciso de tinta lavável para o banheiro"
- "Quero tinta premium para área externa"
- "Que cor combina com móveis brancos?"

### **Conversação (mesmo session_uuid):**
- 1ª: "Preciso de tinta para quarto"
- 2ª: "Me fale mais sobre a opção premium"
- 3ª: "Qual a diferença de preço?"

## 🐛 Troubleshooting

### **Token Expirado:**
- Execute novamente `Authentication > Login - Admin User`

### **Erro 401 Unauthorized:**
- Verifique se o token foi salvo corretamente
- Verifique se os serviços estão rodando

### **Erro de Conexão:**
- Verifique se os serviços estão rodando:
  ```bash
  docker-compose ps
  ```

### **Session UUID não funciona:**
- Verifique se usou o UUID retornado na resposta anterior
- Cada nova conversa (session_uuid: null) cria nova sessão

## 🎨 Scripts Automáticos e Visualização

A coleção inclui scripts que:
- ✅ Salvam automaticamente o token JWT após login (em Collection Variables e Environment)
- ✅ Salvam automaticamente session UUIDs para continuidade de conversa
- ✅ Validam respostas HTTP com testes automáticos
- ✅ Exibem informações úteis no console do Postman
- 🖼️ **NOVO:** Visualizam automaticamente as imagens simuladas no Postman

### 🖼️ Visualização de Simulação de Tinta - Before & After

Quando você executa o endpoint **"Paint Simulation with Image"**, o Postman automaticamente:

**📤 ANTES (Pre-request):**
1. Mostra a imagem de entrada na aba **"Visualize"** 
2. Exibe a mensagem que será enviada
3. Indica que o processamento está em andamento

**🎨 DEPOIS (Response):**
1. Mostra comparação lado a lado: imagem original vs. simulada
2. Exibe a resposta da IA com detalhes
3. Mostra estatísticas (tamanhos dos arquivos, etc.)
4. Layout responsivo e elegante

**Como usar:**
1. Execute `Authentication > Login - Admin User` 
2. Substitua o `image_base64` no body por uma imagem real (ou use a de exemplo)
3. Execute `AI Recommendations > Paint Simulation with Image`
4. **Antes:** Veja a imagem de entrada na aba **"Visualize"**
5. **Depois:** Veja a comparação Before & After na aba **"Visualize"** da resposta

## 📞 Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/auth/login` | POST | Login e obtenção de token |
| `/api/v1/recommend` | POST | Recomendações com IA |
| `/api/v1/search` | POST | Busca direta de produtos |
| `/api/v1/filter` | POST | Filtro de produtos |
| `/api/v1/chat/sessions` | GET | Listar sessões do usuário |
| `/api/v1/chat/reset` | POST | Resetar sessão |
| `/health` | GET | Status dos serviços |

## 🆕 Novos Recursos (v2.0)

### ✨ **Captura Automática de Token Melhorada**
- Token é salvo em **Collection Variables** E **Environment Variables**
- Funciona automaticamente sem configuração adicional
- Logs detalhados com emojis para facilitar debug

### 🔄 **Detecção Automática de Sessão**
- Quando `session_uuid` é `null`, usa automaticamente a sessão mais recente do usuário
- Testa o novo comportamento no endpoint **"Test 4: Auto Session Detection"**

### 🖼️ **Simulação de Tinta com Visualização**
- Endpoint dedicado para testar simulação de imagem
- Visualizador automático na aba "Visualize" do Postman
- Suporte a imagens base64 completas

### 🇧🇷 **Termos em Português**
- Todos os filtros e buscas agora usam termos em português:
  - `interno/externo` ao invés de `internal/external`
  - `fosco/acetinado/semi-brilho/brilhante` ao invés de `matte/satin/etc`
  - `lavável/antimofo` ao invés de `washable/anti-mold`

### 🧪 **Testes Abrangentes**
- Novos testes de persistência de conversa
- Validação automática de respostas
- Scripts de teste para todos os cenários

## 🔧 Resolução de Problemas

### **Token não está sendo salvo automaticamente:**
1. Verifique se executou o request de Login
2. Olhe no Console do Postman - deve aparecer "✅ Token saved successfully!"
3. Verifique nas **Collection Variables** se `access_token` tem valor

### **Visualização de imagem não aparece:**
1. Execute o endpoint "Paint Simulation with Image"
2. **Para imagem de entrada:** Clique na aba **"Visualize"** ANTES de enviar o request
3. **Para resultado:** Aguarde a resposta completa e clique na aba **"Visualize"** da resposta
4. Certifique-se de usar a aba **"Visualize"** (não "Pretty" ou "Raw")
5. Se não aparecer, verifique se `image_base64` (input) e `image_data` (output) existem no JSON

### **Sessão automática não funciona:**
1. Crie uma sessão primeiro (qualquer request com `session_uuid: null`)
2. Em seguida, teste com `session_uuid: null` novamente
3. Deve reutilizar a sessão anterior automaticamente

Agora você tem uma coleção completa e atualizada para testar toda a funcionalidade da API! 🚀