"""Edições diretas no Google Ads via API, com simulação por padrão.

Toda edição roda em modo SIMULAÇÃO (validate_only): o Google valida a mudança e
nada é alterado. Para aplicar de verdade, acrescente --executar.

Exemplos:
    python ads.py contas
    python ads.py campanhas 1234567890
    python ads.py pausar 1234567890 111222333
    python ads.py pausar 1234567890 111222333 --executar
    python ads.py ativar 1234567890 111222333 --executar
    python ads.py orcamento 1234567890 111222333 150.00 --executar
    python ads.py negativar 1234567890 111222333 "gratis" "curso online" --tipo PHRASE --executar
"""
import argparse
import os
import sys

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core import protobuf_helpers

CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "google-ads.yaml")


def limpar_id(valor):
    return valor.replace("-", "").strip()


def consultar(client, customer_id, query):
    ga = client.get_service("GoogleAdsService")
    for lote in ga.search_stream(customer_id=customer_id, query=query):
        yield from lote.results


def aviso(executar):
    print("APLICADO na conta." if executar else "SIMULAÇÃO ok, nada foi alterado. Use --executar para aplicar.")


def cmd_contas(client, args):
    svc = client.get_service("CustomerService")
    for nome in svc.list_accessible_customers().resource_names:
        print(nome.split("/")[-1])


def cmd_campanhas(client, args):
    query = """
        SELECT campaign.id, campaign.name, campaign.status,
               campaign_budget.amount_micros, metrics.cost_micros, metrics.conversions
        FROM campaign
        WHERE campaign.status != 'REMOVED' AND segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC"""
    print(f"{'ID':<14}{'STATUS':<10}{'ORÇ/DIA':>10}{'CUSTO 30D':>12}{'CONV':>8}  NOME")
    for r in consultar(client, args.conta, query):
        print(f"{r.campaign.id:<14}{r.campaign.status.name:<10}"
              f"{r.campaign_budget.amount_micros / 1e6:>10.2f}{r.metrics.cost_micros / 1e6:>12.2f}"
              f"{r.metrics.conversions:>8.1f}  {r.campaign.name}")


def mudar_status(client, args, status):
    svc = client.get_service("CampaignService")
    op = client.get_type("CampaignOperation")
    campanha = op.update
    campanha.resource_name = svc.campaign_path(args.conta, args.campanha)
    campanha.status = client.enums.CampaignStatusEnum[status]
    client.copy_from(op.update_mask, protobuf_helpers.field_mask(None, campanha._pb))
    svc.mutate_campaigns(request={"customer_id": args.conta, "operations": [op],
                                  "validate_only": not args.executar})
    print(f"Campanha {args.campanha} -> {status}.")
    aviso(args.executar)


def cmd_orcamento(client, args):
    query = f"""
        SELECT campaign_budget.resource_name, campaign_budget.amount_micros,
               campaign_budget.explicitly_shared
        FROM campaign WHERE campaign.id = {int(args.campanha)}"""
    linhas = list(consultar(client, args.conta, query))
    if not linhas:
        sys.exit("Campanha não encontrada.")
    orc = linhas[0].campaign_budget
    if orc.explicitly_shared:
        print("ATENÇÃO: orçamento compartilhado, a mudança afeta todas as campanhas que o usam.")
    svc = client.get_service("CampaignBudgetService")
    op = client.get_type("CampaignBudgetOperation")
    novo = op.update
    novo.resource_name = orc.resource_name
    novo.amount_micros = round(args.valor * 1_000_000)
    client.copy_from(op.update_mask, protobuf_helpers.field_mask(None, novo._pb))
    svc.mutate_campaign_budgets(request={"customer_id": args.conta, "operations": [op],
                                         "validate_only": not args.executar})
    print(f"Orçamento diário: {orc.amount_micros / 1e6:.2f} -> {args.valor:.2f}.")
    aviso(args.executar)


def cmd_negativar(client, args):
    svc = client.get_service("CampaignCriterionService")
    campanha = client.get_service("CampaignService").campaign_path(args.conta, args.campanha)
    ops = []
    for termo in args.termos:
        op = client.get_type("CampaignCriterionOperation")
        crit = op.create
        crit.campaign = campanha
        crit.negative = True
        crit.keyword.text = termo
        crit.keyword.match_type = client.enums.KeywordMatchTypeEnum[args.tipo]
        ops.append(op)
    svc.mutate_campaign_criteria(request={"customer_id": args.conta, "operations": ops,
                                          "validate_only": not args.executar})
    print(f"{len(ops)} negativa(s) {args.tipo} na campanha {args.campanha}: {', '.join(args.termos)}.")
    aviso(args.executar)


def main():
    p = argparse.ArgumentParser(description="Edições no Google Ads via API.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("contas", help="lista as contas acessíveis")
    s = sub.add_parser("campanhas", help="lista campanhas e números de 30 dias")
    s.add_argument("conta")
    for nome in ("pausar", "ativar"):
        s = sub.add_parser(nome, help=f"{nome} uma campanha")
        s.add_argument("conta")
        s.add_argument("campanha")
        s.add_argument("--executar", action="store_true")
    s = sub.add_parser("orcamento", help="altera o orçamento diário de uma campanha")
    s.add_argument("conta")
    s.add_argument("campanha")
    s.add_argument("valor", type=float)
    s.add_argument("--executar", action="store_true")
    s = sub.add_parser("negativar", help="adiciona palavras negativas na campanha")
    s.add_argument("conta")
    s.add_argument("campanha")
    s.add_argument("termos", nargs="+")
    s.add_argument("--tipo", choices=["BROAD", "PHRASE", "EXACT"], default="PHRASE")
    s.add_argument("--executar", action="store_true")
    args = p.parse_args()

    if hasattr(args, "conta"):
        args.conta = limpar_id(args.conta)
    if not os.path.exists(CONFIG):
        sys.exit(f"Arquivo {CONFIG} não encontrado. Copie google-ads.template.yaml e preencha.")
    client = GoogleAdsClient.load_from_storage(CONFIG)

    acoes = {"contas": cmd_contas, "campanhas": cmd_campanhas, "orcamento": cmd_orcamento,
             "negativar": cmd_negativar,
             "pausar": lambda c, a: mudar_status(c, a, "PAUSED"),
             "ativar": lambda c, a: mudar_status(c, a, "ENABLED")}
    try:
        acoes[args.cmd](client, args)
    except GoogleAdsException as ex:
        print(f"Erro da API (request_id {ex.request_id}):")
        for erro in ex.failure.errors:
            print(f"  - {erro.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
