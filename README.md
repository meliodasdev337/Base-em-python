Base.py 🤖

Um bot Discord moderno e completo desenvolvido em Python usando Discord.py, com interface interativa, IA integrada e sistema de moderação.

Funcionalidades

Comandos de Usuário

· /ping - Painel de status interativo com latência, uptime e status da API Discord
· /userinfo - Informações detalhadas sobre usuários (cargos, badges, status, atividade)
· /creditos - Informações sobre o criador e links importantes

Comandos de Moderação

· /ban - Banir usuários com motivo e confirmação
· /unban - Remover banimento por ID
· /lock - Trancar/destrancar canais com botão interativo

IA Integrada

· Respostas inteligentes quando o bot é mencionado
· Usa Mistral AI API para respostas contextuais
· Personalidade customizada como assistente do Discord

Recursos Extras

· Sistema de emojis personalizados automático
· MongoDB integrado para futuras funcionalidades
· Interface com botões e menus interativos
· Status customizável via config.json

Instalação

1. Pré-requisitos

· Python 3.11 ou superior
· Conta no Discord Developer Portal
· Token do bot Discord
· (Opcional) Chave da API Mistral AI

2. Clonar o repositório

```bash
git clone https://github.com/meliodasdev337/base-bot.git
cd base-bot
```

3. Instalar dependências

```bash
pip install -r requirements.txt
```

4. Configurar o bot

1. Crie um arquivo config.json na raiz do projeto: (já vai estar criado apenas se não estiver.)

```json
{
  "token": "SEU_TOKEN_DO_BOT_AQUI",
  "guild_id": "ID_DO_SEU_SERVIDOR",
  "owners": ["SEU_ID_DO_DISCORD"],
  "mistral_api_key": "SUA_CHAVE_MISTRAL_AI",
  "status": {
    "type": "watching",
    "text": "Base Meliodas"
  }
}
```

1. Para obter a chave da Mistral AI:
   · Acesse: https://console.mistral.ai/build/agents?workspace_dialog=apiKeys
   · Faça login/crie uma conta
   · Clique em "Create new key"
   · Copie a chave gerada
   · Cole no config.json como "mistral_api_key"
2. Configurar emojis personalizados:
   · Coloque suas imagens de emoji em database/emojis.json
   · Formato:
   ```json
   [
     {
       "name": "nome_emoji",
       "image": "url_da_imagem"
     }
   ]
   ```

5. Executar o bot

```bash
python main.py
```

Estrutura do Projeto

```
base-bot/
├── commands/           # Comandos slash
│   ├── user/          # Comandos para usuários
│   └── admin/         # Comandos de moderação
├── events/            # Eventos do bot
│   ├── bot/           # Eventos do bot
│   └── mensagem/      # Eventos de mensagem
├── functions/         # Funções utilitárias
│   ├── emojis.py      # Sistema de emojis
│   └── mongo.py       # Conexão com MongoDB
├── utils/             # Utilitários
│   └── ai.py          # Integração com IA
├── database/          # Arquivos de dados
├── main.py           # Arquivo principal
├── config.json       # Configurações
└── requirements.txt  # Dependências
```

Configuração Avançada

Configuração de Status

No config.json, você pode customizar o status do bot:

```json
"status": {
  "type": "playing",  // playing, watching, listening, streaming
  "text": "Base Meliodas"
}
```

Sistema de Emojis

O bot automaticamente:

1. Busca emojis em database/emojis.json
2. Faz upload para o Discord
3. Salva os IDs em database/emojis_ids.json
4. Usa esses emojis em todos os comandos

Integração com IA

Para usar a IA:

1. Obtenha uma chave da Mistral AI
2. Configure no config.json
3. Mencione o bot em qualquer canal
4. Ele responderá com IA

Proteção de Créditos

O bot inclui um sistema de verificação de integridade que:

· Verifica se os créditos do criador (Meliodas) estão intactos
· Impede a inicialização se arquivos essenciais forem removidos
· Garante que o comando /creditos sempre mostre o criador original

Suporte

· Criador: Meliodas (Discord: @wwttzim)
· GitHub: https://github.com/meliodasdev337
· Servidor Discord: https://discord.gg/awsupjWb9x
· Base pública: https://github.com/meliodasdev337/Base-em-python

Licença

Este projeto é de código aberto. Você pode usá-lo, modificá-lo e distribuí-lo livremente, mas deve manter os créditos ao criador original (Meliodas) no comando /creditos.

Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Reportar bugs
2. Sugerir novas funcionalidades
3. Enviar pull requests

Criado com ❤️ por Meliodas