# Biblioteca GAQL (use com a ferramenta `search`: `customer_id` + `query`)

## Campanhas ativas, últimos 30 dias
SELECT campaign.id, campaign.name, campaign.status, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.cost_per_conversion
FROM campaign
WHERE campaign.status = 'ENABLED' AND segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC

## Termos de pesquisa (desperdício e negativação)
SELECT search_term_view.search_term, campaign.name, metrics.clicks, metrics.cost_micros, metrics.conversions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS AND metrics.clicks > 0
ORDER BY metrics.cost_micros DESC
LIMIT 100

## Quality Score por palavra-chave
SELECT ad_group_criterion.keyword.text, ad_group_criterion.quality_info.quality_score, ad_group_criterion.quality_info.creative_quality_score, ad_group_criterion.quality_info.post_click_quality_score, ad_group_criterion.quality_info.search_predicted_ctr, campaign.name
FROM keyword_view
WHERE ad_group_criterion.status = 'ENABLED'
ORDER BY ad_group_criterion.quality_info.quality_score ASC

## CPA por grupo de anúncios
SELECT ad_group.name, campaign.name, metrics.cost_micros, metrics.conversions, metrics.cost_per_conversion
FROM ad_group
WHERE segments.date DURING LAST_30_DAYS AND metrics.conversions > 0
ORDER BY metrics.cost_per_conversion ASC

## Performance por dispositivo
SELECT campaign.name, segments.device, metrics.clicks, metrics.cost_micros, metrics.conversions
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
