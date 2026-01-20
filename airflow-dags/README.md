# Airflow DAGs - Orquestração de Pipelines

Este diretório organiza as DAGs (Directed Acyclic Graphs) do Apache Airflow utilizadas para orquestração de pipelines de dados e automações do projeto Yduqs. A separação por ambiente garante isolamento adequado entre desenvolvimento, testes e produção.

## Estrutura por Ambiente

A organização em subdiretórios distintos para UAT e Produção permite que cada ambiente mantenha suas próprias configurações, variáveis e versões de DAGs. Esta separação é fundamental para garantir que testes e validações sejam realizados adequadamente antes de promover mudanças para produção.

O ambiente de UAT serve como espaço de validação onde novas DAGs e modificações podem ser testadas com dados reais ou sintéticos antes de impactar processos produtivos. Apenas após validação completa neste ambiente as DAGs devem ser promovidas para produção.

## Desenvolvimento de DAGs

Cada DAG deve ser desenvolvida seguindo as melhores práticas do Airflow, incluindo uso apropriado de operadores, definição clara de dependências entre tarefas e configuração adequada de scheduling. As DAGs devem ser idempotentes sempre que possível, permitindo reexecução sem efeitos colaterais indesejados.

A documentação inline é fundamental para manutenção futura. Utilize docstrings detalhadas explicando o propósito da DAG, suas dependências externas, dados que processa e impacto esperado. Defina owners claramente para cada DAG, facilitando identificação de responsáveis em caso de falhas ou dúvidas.

## Gerenciamento de Segredos

Nunca armazene credenciais, tokens ou senhas diretamente nas DAGs. Utilize Airflow Variables e Connections em conjunto com backends seguros como Google Secret Manager. Esta prática garante que segredos sejam gerenciados centralizadamente e possam ser rotacionados sem modificar código.

Para deploys automatizados, configure integração entre Airflow e Secret Manager permitindo que DAGs acessem credenciais necessárias de forma segura em runtime. Documente quais secrets cada DAG necessita para facilitar troubleshooting e configuração em novos ambientes.

## Deployment e Versionamento

As DAGs devem ser versionadas junto com o restante do código, permitindo rastreamento de mudanças e rollback quando necessário. Para deployment em Cloud Composer ou ambientes Airflow gerenciados, utilize processos automatizados que validem sintaxe e dependências antes de efetivar mudanças.

Mantenha histórico de mudanças documentado, incluindo motivação para alterações, impacto esperado e procedimentos de rollback. Esta documentação é essencial para auditorias e para entendimento de evolução do sistema ao longo do tempo.

## Monitoramento e Alertas

Configure alertas apropriados para falhas de DAGs críticas, utilizando callbacks do Airflow para notificar equipes responsáveis via email, Slack ou outros canais. Monitore tempos de execução para identificar degradações de performance que possam indicar problemas upstream ou necessidade de otimização.

Logs estruturados devem ser implementados para facilitar debugging e análise de execuções. Utilize logging levels apropriados e inclua contexto suficiente para rastreamento de problemas sem sobrecarregar os sistemas de log.
