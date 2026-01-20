# Airflow UAT - Ambiente de Testes e Validação

Este diretório contém DAGs e configurações específicas para o ambiente de UAT (User Acceptance Testing) do Apache Airflow. O ambiente UAT serve como espaço controlado para validação de novas DAGs, modificações em pipelines existentes e testes de integração antes de promoção para produção.

## Propósito do Ambiente

O ambiente UAT permite validação completa de mudanças em pipelines de dados sem risco de impactar processos produtivos. Aqui podem ser testadas novas lógicas de processamento, validadas integrações com novos sistemas e verificadas correções de bugs antes de deployment em produção.

Este ambiente deve espelhar configurações produtivas o mais fielmente possível, mantendo diferenças apenas onde necessário para isolamento. Utilize dados de teste ou subconjuntos de dados produtivos quando possível, garantindo testes realistas sem comprometer sensibilidade de informações.

## Ciclo de Desenvolvimento

Novas DAGs ou modificações significativas devem primeiro ser desenvolvidas e testadas localmente quando possível. Após validação local básica, deploy para UAT permite testes mais completos em ambiente que replica infraestrutura produtiva.

Mantenha DAGs em UAT até que validação completa seja realizada, incluindo testes de casos extremos, validação de tratamento de erros e verificação de performance. Apenas após aprovação formal as mudanças devem ser promovidas para produção.

## Configurações e Variáveis

Variáveis e conexões do Airflow devem ser configuradas especificamente para UAT, apontando para recursos de teste ao invés de sistemas produtivos quando apropriado. Documente claramente quais variáveis diferem entre ambientes e razões para estas diferenças.

Secrets e credenciais devem ser gerenciados via Secret Manager mesmo em UAT, mantendo práticas seguras de gerenciamento de informações sensíveis. Utilize service accounts dedicadas ao ambiente de teste, limitando permissões ao mínimo necessário.

## Validação e Promoção

Estabeleça checklist de validação que deve ser completado antes de promover mudanças para produção. Este checklist pode incluir execução bem-sucedida end-to-end, validação de qualidade de dados processados, verificação de tratamento apropriado de erros, confirmação de performance aceitável e aprovação de stakeholders relevantes.

Documente resultados de testes realizados em UAT, facilitando rastreamento de validações executadas e decisões de promoção para produção. Mantenha histórico destas validações para referência futura e aprendizado.

## Limpeza e Manutenção

Revise periodicamente DAGs em UAT, removendo aquelas que já foram promovidas para produção ou abandonadas. Manter ambiente limpo facilita navegação e reduz confusão sobre quais DAGs estão ativamente sendo testadas.

Para DAGs de longa duração em UAT, documente status e próximos passos necessários para conclusão de testes e eventual promoção ou descarte. Esta documentação mantém transparência sobre progresso de desenvolvimento.
