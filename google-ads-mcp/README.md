# Google Ads MCP: setup rápido (Daniel)

Pré-requisitos: Python 3.12+ e pipx.

1. `pipx install google-ads-mcp && pipx ensurepath` (reabra o terminal)
2. Credenciais (5): Developer Token (API Center da MCC), OAuth Client ID/Secret (Google Cloud, app Desktop), Refresh Token, Customer ID e Login Customer ID (10 dígitos, sem hífen).
3. Copie `claude_desktop_config.template.json` para:
   - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
   - Windows: %APPDATA%\Claude\claude_desktop_config.json
   e preencha os valores. NUNCA commite o arquivo preenchido.
4. Reinicie o Claude Desktop por completo.
5. Teste: "Liste as contas acessíveis do Google Ads" e depois use as consultas de `queries.gaql.md`.

Servidor somente leitura: não altera lances nem campanhas.
