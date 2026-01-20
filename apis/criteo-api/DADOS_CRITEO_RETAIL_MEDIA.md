# Dados Extraíveis da API Criteo Retail Media

Fonte: https://developers.criteo.com/retail-media/docs/metrics-and-dimensions

## 1. DADOS DE CONTAS (list_accounts)

Informações sobre contas de anunciantes:
- ID da conta
- Nome da conta
- Tipo de conta (supply/demand)

## 2. DADOS DE CAMPANHAS (list_campaigns)

Informações sobre campanhas:
- ID da campanha
- Nome da campanha
- Status da campanha
- Tipo de campanha
- Datas de início/fim
- Orçamento
- Configurações de atribuição

## 3. MÉTRICAS DE RELATÓRIOS

### Métricas de Performance
| Métrica | Descrição |
|---------|-----------|
| `clicks` | Cliques em anúncios (gera custo para campanhas de leilão aberto) |
| `impressions` | Impressões de anúncios renderizados na página |
| `placementImpressions` | Impressões de placement (para Preferred Deals) |
| `productImpressions` | Impressões de produto (para Open Auction) |
| `cpc` | Custo por clique médio (spend / clicks) |
| `cpm` | Custo por mil impressões |
| `cpo` | Custo por pedido (spend / attributedOrders) |
| `ctr` | Taxa de cliques (clicks / impressions) |
| `frequency` | Frequência média de exibição para o mesmo usuário |
| `spend` | Gasto total da campanha |
| `uniqueVisitors` | Visitantes únicos |

### Métricas de Conversão/Vendas
| Métrica | Descrição |
|---------|-----------|
| `attributedSales` | Vendas atribuídas diretamente à campanha |
| `attributedOrders` | Pedidos atribuídos a cliques ou impressões |
| `attributedUnits` | Unidades vendidas atribuídas |
| `assistedSales` | Vendas assistidas (não foram a última interação) |
| `assistedUnits` | Unidades assistidas na venda |
| `roas` | Return on Ad Spend (attributedSales / spend) |

### Métricas de Capout (Limite de Orçamento)
| Métrica | Descrição |
|---------|-----------|
| `capoutHour` | Hora média do dia em que o line item atingiu o limite |
| `capoutMissedClicks` | Cliques estimados perdidos por atingir limite |
| `capoutMissedImpressions` | Impressões estimadas perdidas |
| `capoutMissedSales` | Vendas estimadas perdidas |
| `capoutMissedSpend` | Gasto estimado perdido |
| `capoutMissedTraffic` | Percentual de tráfego perdido |

## 4. DIMENSÕES DE RELATÓRIOS

### Dimensões de Conta/Campanha
| Dimensão | Descrição |
|----------|-----------|
| `accountId` | ID da conta do relatório |
| `accountName` | Nome da conta (supply ou demand) |
| `campaignId` | ID da campanha |
| `campaignName` | Nome da campanha |
| `campaignTypeName` | Tipo de campanha (Open Auction ou Preferred Deals) |

### Dimensões de Line Item
| Dimensão | Descrição |
|----------|-----------|
| `lineItemId` | ID do line item |
| `lineItemName` | Nome do line item |

### Dimensões de Produto
| Dimensão | Descrição |
|----------|-----------|
| `advProductId` | ID do produto anunciado |
| `advProductName` | Nome do produto anunciado |
| `advProductCategory` | Categoria do produto anunciado |
| `brandId` | ID da marca do produto |
| `brandName` | Nome da marca do produto |

### Dimensões de Criativo (Display Campaigns)
| Dimensão | Descrição |
|----------|-----------|
| `creativeId` | ID do criativo |
| `creativeName` | Nome do criativo |
| `creativeTemplateId` | ID do template do criativo |
| `creativeTemplateName` | Nome do template (FlagShip, Showcase, SponsoredProducts, etc.) |
| `creativeTypeId` | ID do tipo de criativo |
| `creativeTypeName` | Tipo de criativo (Commerce Display, Commerce Video, etc.) |

### Dimensões Temporais
| Dimensão | Descrição |
|----------|-----------|
| `date` | Data do relatório |
| `advDate` | Data em que o anúncio foi entregue |
| `advHour` | Hora em que o anúncio foi entregue |

### Dimensões de Contexto
| Dimensão | Descrição |
|----------|-----------|
| `pageType` | Tipo de página onde o anúncio apareceu |
| `keyword` | Palavra-chave que acionou o anúncio |
| `servedCategory` | Categoria servida |
| `environment` | Ambiente (web, app, etc.) |

### Dimensões de Transação (attributedTransactions)
| Dimensão | Descrição |
|----------|-----------|
| `activitySellerId` | ID do vendedor responsável pelo evento |
| `activitySellerName` | Nome do vendedor responsável pelo evento |
| `saleSellerId` | ID do vendedor responsável pela venda |
| `saleSellerName` | Nome do vendedor responsável pela venda |

## 5. TIPOS DE RELATÓRIO

| Tipo | Descrição |
|------|-----------|
| `summary` | Resumo geral de performance |
| `pageType` | Análise por tipo de página |
| `keyword` | Análise por palavra-chave |
| `product` | Análise por produto |
| `product category` | Análise por categoria de produto |
| `served category` | Análise por categoria servida |
| `environment` | Análise por ambiente |
| `attributedTransactions` | Transações atribuídas detalhadas |
| `capout` | Análise de limite de orçamento |
| `Flexible reporting` | Relatório customizado |

## 6. NÍVEIS DE RELATÓRIO

- **Campaign**: Dados agregados por campanha
- **Line-item**: Dados detalhados por line item

## 7. CONFIGURAÇÕES DE ATRIBUIÇÃO

| Parâmetro | Valores | Descrição |
|-----------|---------|-----------|
| `clickAttributionWindow` | 1D, 7D, 14D, 30D | Janela de atribuição de cliques |
| `viewAttributionWindow` | 1D, 7D, 14D, 30D | Janela de atribuição de visualizações |
| `salesChannel` | all, online, offline | Canal de vendas |
| `campaignType` | all, auction, preferredDeals | Tipo de campanha |

## 8. ENDPOINTS DA API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/oauth2/token` | POST | Autenticação OAuth2 |
| `/retail-media/accounts` | GET | Listar contas |
| `/retail-media/accounts/{id}/campaigns` | GET | Listar campanhas |
| `/retail-media/reports/campaigns` | POST | Solicitar relatório |
| `/retail-media/reports/{id}/status` | GET | Verificar status |
| `/retail-media/reports/{id}/output` | GET | Baixar relatório |
