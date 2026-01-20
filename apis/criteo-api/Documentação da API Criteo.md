# Documentação da API Criteo

Este documento fornece uma explicação detalhada de como usar o módulo Python para interagir com a API Criteo, com base nos arquivos `Criteo.py` e `README.md` fornecidos.

## Visão Geral

O módulo Python `Criteo` serve como um wrapper para a API REST da Criteo, simplificando o processo de autenticação e extração de dados. Ele foi projetado para retornar dados em um formato de DataFrame do Pandas, facilitando a análise e o processamento de dados.

## Instalação e Inicialização

Para começar, você precisa ter o módulo `cadastra_core` instalado em seu ambiente Python. Em seguida, você pode importar a classe `Criteo` e instanciá-la com suas credenciais.

### Credenciais Necessárias

- `client_id`: Seu ID de cliente da Criteo.
- `client_secret`: Sua chave secreta de cliente da Criteo.
- `refresh_token`: Seu token de atualização da Criteo.

### Exemplo de Inicialização

```python
from cadastra_core import Criteo

# Suas credenciais
client_id = 'SEU_CLIENT_ID'
client_secret = 'SEU_CLIENT_SECRET'
refresh_token = 'SEU_REFRESH_TOKEN'

# Instanciando a classe Criteo
criteo = Criteo(client_id, client_secret, refresh_token)
```

## Autenticação

O processo de autenticação é tratado automaticamente pela classe `Criteo` durante a inicialização. O método `request_access_token` é chamado para obter um `access_token` usando o `refresh_token` fornecido. Este `access_token` é então usado para autenticar todas as chamadas subsequentes à API.

## Métodos Disponíveis

A classe `Criteo` fornece vários métodos para interagir com a API da Criteo. Abaixo estão os principais métodos e como usá-los.

### `list_accounts()`

Este método lista todas as contas de anunciantes disponíveis associadas às suas credenciais.

**Exemplo:**

```python
criteo.list_accounts()
```

### `list_campaigns(account_id)`

Este método recupera uma lista de todas as campanhas para uma determinada `account_id`.

**Parâmetros:**

- `account_id` (str): O ID da conta para a qual você deseja listar as campanhas.

**Exemplo:**

```python
df_campanhas = criteo.list_campaigns(account_id="123456")
print(df_campanhas)
```

### `get_campaigns_ids(account_id, status)`

Este método retorna uma lista de IDs de campanha para uma determinada `account_id`, com a opção de filtrar por status.

**Parâmetros:**

- `account_id` (str): O ID da conta.
- `status` (str, opcional): Filtra as campanhas por status (por exemplo, "running", "ended").

**Exemplo:**

```python
ids_campanhas_ativas = criteo.get_campaigns_ids(account_id="123456", status="running")
print(ids_campanhas_ativas)
```

### `request_report(...)`

Este é o método mais complexo, usado para solicitar relatórios de forma assíncrona. Ele inicia um trabalho de relatório na Criteo e, em seguida, aguarda a conclusão do relatório antes de baixar os dados.

**Parâmetros:**

- `dimensions` (list[str]): As dimensões para o seu relatório (por exemplo, `["date", "lineItemName"]`).
- `metrics` (list[str]): As métricas que você deseja incluir (por exemplo, `["clicks", "spend", "impressions"]`).
- `start_date` (str): A data de início do relatório no formato 'YYYY-MM-DD'.
- `end_date` (str): A data de término do relatório no formato 'YYYY-MM-DD'.
- `account_id` (str): O ID da conta para a qual o relatório está sendo solicitado.
- Outros parâmetros opcionais, como `clickAttributionWindow`, `viewAttributionWindow`, `campaign_type`, etc.

**Processo de Geração de Relatório:**

1.  **Solicitação do Relatório:** O método `request_report` primeiro envia uma solicitação POST para a API da Criteo para criar um trabalho de relatório.
2.  **Verificação de Status:** Em seguida, ele entra em um loop, chamando o método `check_report_status` para verificar o status do trabalho do relatório. O loop continua até que o status seja "success" ou que o tempo máximo de espera seja atingido.
3.  **Download do Relatório:** Assim que o relatório for bem-sucedido, o método `download_report` é chamado para buscar os dados do relatório e retorná-los como um DataFrame do Pandas.

**Exemplo:**

```python
dimensoes = ["date", "lineItemName"]
metricas = ["clicks", "spend", "impressions"]
data_inicio = "2024-09-01"
data_fim = "2024-12-05"

df_relatorio = criteo.request_report(
    dimensions=dimensoes,
    metrics=metricas,
    start_date=data_inicio,
    end_date=data_fim,
    account_id="123456"
)

print(df_relatorio)
```

## Conclusão

Este módulo Python fornece uma interface conveniente e fácil de usar para a API da Criteo. Ao encapsular a lógica de autenticação e geração de relatórios, ele permite que os desenvolvedores se concentrem na extração e análise de dados, em vez de nos detalhes de baixo nível da integração da API.
