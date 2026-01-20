# Infraestrutura - Configurações e Recursos

Este diretório centraliza artefatos relacionados à infraestrutura do projeto Yduqs, incluindo scripts de provisionamento, configurações de serviços e documentação de recursos cloud. A organização adequada destes elementos é fundamental para manutenção eficiente e segura da infraestrutura.

## Secure Store - Gerenciamento de Exemplos

O subdiretório `secure_store` serve como local para armazenamento de templates e exemplos de arquivos de configuração que contenham estruturas sensíveis. É fundamental destacar que este diretório nunca deve conter credenciais, chaves ou tokens reais.

Todos os arquivos armazenados aqui devem utilizar o sufixo `.example` para indicar claramente que são modelos, não credenciais reais. Por exemplo, um arquivo de service account do Google Cloud deve ser nomeado como `service-account.example.json`, contendo apenas a estrutura esperada com valores fictícios.

Esta prática permite que desenvolvedores entendam quais configurações são necessárias sem expor informações sensíveis no repositório. O `.gitignore` está configurado para bloquear commit de arquivos reais, mas desenvolvedores devem sempre verificar antes de commitar qualquer arquivo neste diretório.

## Credenciais Reais - Onde Armazenar

Credenciais e segredos reais devem ser armazenados exclusivamente em Google Secret Manager, AWS Secrets Manager ou serviços equivalentes. Para ambientes de desenvolvimento local, utilize arquivos de configuração que não sejam versionados, referenciando variáveis de ambiente que apontam para os secrets apropriados.

Nunca armazene credenciais em buckets públicos, repositórios git ou sistemas de arquivos compartilhados sem criptografia apropriada. Para deploys automatizados, configure integração segura entre pipelines de CI/CD e gerenciadores de secrets, garantindo que credenciais sejam injetadas em runtime sem serem expostas em logs ou artefatos de build.

## Infraestrutura como Código

Para provisionamento de recursos cloud, utilize ferramentas de Infrastructure as Code como Terraform, Pulumi ou scripts de gcloud/AWS CLI versionados neste diretório. Mantenha estados remotos em backends seguros e utilize workspaces ou diretórios separados para ambientes distintos.

Documente dependências entre recursos e ordem de provisionamento necessária. Inclua instruções claras de setup inicial, incluindo configuração de credentials, inicialização de backends e validação de configurações antes de aplicar mudanças.

## Segurança e Auditoria

Configure logging e auditoria apropriados para todas as operações de infraestrutura. Utilize IAM policies seguindo princípio de menor privilégio, garantindo que cada serviço e usuário tenha apenas as permissões estritamente necessárias para suas funções.

Revise periodicamente permissões e acessos, removendo credenciais e contas não utilizadas. Implemente rotação automática de secrets quando possível e monitore tentativas de acesso não autorizado para identificar potenciais brechas de segurança.
