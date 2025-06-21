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

## 🎨 Scripts Automáticos

A coleção inclui scripts que:
- ✅ Salvam automaticamente o token JWT após login
- ✅ Salvam automaticamente session UUIDs
- ✅ Validam respostas HTTP
- ✅ Exibem informações úteis no console

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

Agora você tem uma coleção completa para testar toda a funcionalidade da sua API! 🚀