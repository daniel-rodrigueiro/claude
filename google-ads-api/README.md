# Google Ads API: edições diretas na MCC (guia para iniciante)

## Por que não o MCP oficial
O `google-ads-mcp` (pasta `../google-ads-mcp`) é **somente leitura**: consulta, não edita.
Para pausar, ativar, mudar orçamento e negativar, usamos a biblioteca oficial `google-ads`
(Python) com o script `ads.py` desta pasta.

Regra de segurança do `ads.py`: **toda edição é simulação por padrão** (`validate_only`).
O Google valida a mudança e não altera nada. Só aplica com `--executar`.

---

## Mapa da integração (5 credenciais)

| Credencial | Onde nasce | Status |
|---|---|---|
| Developer Token | Google Ads > Central de API (MCC) | OK (nível Conta de teste) |
| Client ID + Client Secret | Google Cloud > Credenciais OAuth | a fazer |
| Refresh Token | `gerar_refresh_token.py` (login no navegador) | a fazer |
| Login Customer ID | ID da sua MCC (10 dígitos, sem hífen) | você já tem |

---

## Etapa 1: Nível de acesso (Developer Token)
Hoje o token só funciona em **contas de teste**. Para editar contas reais, peça **Acesso básico**.
**Importante:** como você vai EDITAR, a solicitação precisa dizer que a ferramenta faz
gestão (edições), não apenas relatórios. Declarar "read-only" e depois editar contraria o
que foi aprovado. Use o texto da seção "Texto da solicitação" no fim deste arquivo.

Enquanto o acesso básico não sai, pratique numa **MCC de teste**:
1. Saia da conta, crie uma MCC nova em https://ads.google.com/home/tools/manager-accounts/
   e, na criação, escolha "conta de teste" (aparece um selo vermelho "Conta de teste").
2. Dentro dela, crie uma conta de cliente de teste e uma campanha de pesquisa qualquer.
3. Seu token atual já funciona nela. Use o ID da MCC de teste como `login_customer_id`.

## Etapa 2: Projeto no Google Cloud
1. https://console.cloud.google.com > seletor de projeto > **Novo projeto** (ex.: `google-ads-api`).
2. **APIs e serviços > Biblioteca** > pesquise **Google Ads API** > **Ativar**.

## Etapa 3: Tela de consentimento OAuth
1. **APIs e serviços > Tela de consentimento OAuth** (ou "Google Auth Platform").
2. Tipo de usuário: **Externo**. Nome do app, e-mail de suporte e e-mail do desenvolvedor.
3. Em **Público-alvo**, clique em **Publicar app** (status "Em produção").
   Se ficar em "Teste", o Refresh Token **expira em 7 dias**. Pode aparecer o aviso de app não
   verificado: para uso próprio não precisa verificar, basta clicar em "Avançado > Acessar".

## Etapa 4: Client ID e Client Secret
1. **APIs e serviços > Credenciais > Criar credenciais > ID do cliente OAuth**.
2. Tipo: **App para computador**. Crie e clique em **Baixar JSON**.
3. Salve o arquivo nesta pasta como `client_secret.json` (o `.gitignore` já o protege).

## Etapa 5: Instalar na sua máquina
Pré-requisito: Python 3.12+ (https://www.python.org/downloads, marque "Add to PATH" no Windows).
No terminal, dentro desta pasta:
```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS:  source .venv/bin/activate
pip install -r requirements.txt
```

## Etapa 6: Refresh Token
```bash
python gerar_refresh_token.py client_secret.json
```
Abre o navegador: entre com o **mesmo e-mail que tem acesso à MCC**, aceite o escopo do
Google Ads. O terminal imprime `client_id`, `client_secret` e `refresh_token`.

## Etapa 7: Arquivo de configuração
Copie `google-ads.template.yaml` para `google-ads.yaml` e preencha os 5 campos.
Este arquivo é a chave da sua MCC: nunca envie para ninguém nem para o GitHub.

## Etapa 8: Primeiro teste (só leitura)
```bash
python ads.py contas                    # lista os IDs que você acessa
python ads.py campanhas 1234567890      # campanhas de uma conta (ID do cliente)
```

## Etapa 9: Edições
Sempre rode primeiro SEM `--executar` (simulação), confira, e depois com `--executar`.
```bash
python ads.py pausar     1234567890 111222333
python ads.py ativar     1234567890 111222333 --executar
python ads.py orcamento  1234567890 111222333 150.00 --executar
python ads.py negativar  1234567890 111222333 "gratis" "vagas" --tipo PHRASE --executar
```
`1234567890` = conta do cliente (não a MCC). `111222333` = ID da campanha (sai no `campanhas`).

## Etapa 10: Usar com Claude
Instale o Claude Code na sua máquina e abra-o nesta pasta. Peça em linguagem natural
("pause a campanha X do cliente Y", "negative estes termos"): ele roda o `ads.py`, mostra a
simulação e só executa com o seu OK. Para novas edições (lances, anúncios, palavras-chave,
extensões), peça para ele adicionar um comando novo ao `ads.py`, sempre com simulação.

---

## Erros comuns
| Erro | Causa | Solução |
|---|---|---|
| `DEVELOPER_TOKEN_NOT_APPROVED` | Token em nível teste numa conta real | Aguardar acesso básico ou usar MCC de teste |
| `USER_PERMISSION_DENIED` | `login_customer_id` errado ou ausente | Usar o ID da MCC, sem hífen |
| `invalid_grant` | Refresh Token expirado/revogado | App em produção (Etapa 3) e gerar de novo |
| `CUSTOMER_NOT_FOUND` / `INVALID_CUSTOMER_ID` | ID com hífen ou de outra MCC | Conferir com `python ads.py contas` |

---

## Texto da solicitação de Acesso básico (versão para edições)
```
Company: Secchi Rodrigueiro Serviços Digitais Ltda, a digital marketing agency (SEM / paid media) based in Brazil.
Website: https://centro.saocaetanoguiase.com.br

TOOL DESCRIPTION
Internal campaign management tool used only by our own staff to manage the Google Ads accounts of our clients, which are linked to our Manager (MCC) account. It is not offered to third parties, is not a SaaS product and does not resell API access. It is a command-line tool built on the official google-ads Python client library, operated by our team with the help of an AI assistant (Claude) on our own workstation.

API USAGE
- Reporting: GAQL queries (Search / SearchStream) on campaigns, ad groups, keywords, search terms, budgets and conversions.
- Management: pausing and enabling campaigns, updating campaign budgets, and adding negative keywords. We plan to add keyword, ad and bid management over time.
- Every change is first sent with validate_only=true and reviewed by a team member before it is applied. Changes are made only on accounts whose owners have granted us access.

DATA HANDLING AND SECURITY
Credentials are stored only in a local configuration file on our workstation and are never shared or committed to repositories. Report data is used only to manage and report performance to the client who owns the account.

EXPECTED VOLUME
Low: a few hundred operations per day at most.
```
