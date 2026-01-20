# Repositório Principal - Projeto Yduqs

Este repositório é o ponto único de verdade (single source of truth) para códigos, automações, DAGs, documentações e materiais relacionados ao projeto Yduqs. Aqui organizamos artefatos compartilhados entre marcas, pipelines e aplicações.

> Observação de segurança: este README descreve onde os artefatos sensíveis devem estar armazenados e como nomeamos pastas. NUNCA comite em repositórios públicos chaves, tokens ou arquivos sensíveis. Utilize o Google Secret Manager, IAM e buckets privados do GCP para guardar segredos. Arquivos com credenciais só devem existir em ambientes seguros (ex.: storage privativo) e devem ser referenciados via variáveis de ambiente ou secret manager.

## Resumo das mudanças solicitadas

- O diretório que antes era exposto como `secret` foi renomeado para um nome não autoexplicativo para reduzir exposição direta (ver seção Infra).
- O diretório das DAGs do Airflow foi padronizado como `airflow-dags` e separado por ambiente.
- O diretório `guides` foi renomeado para `knowledge-base` para melhor refletir uma biblioteca de conteúdo técnico e compartilhamento.

## Estrutura recomendada de pastas

```
├── brands/
│   ├── wyden/       -> Recursos e configurações específicas da marca Wyden
│   ├── estacio/     -> Recursos e configurações específicas da marca Estácio
│   ├── idomed/      -> Recursos e configurações específicas da marca Idomed
│   └── ibmec/       -> Recursos e configurações específicas da marca Ibmec
│
├── apis/            -> Código das APIs (microsserviços, cloud functions, SDKs, exemplos de deploy)
│
├── docs/            -> Documentações técnicas, textos, anexos, manuais e especificações
│
├── attachments/     -> Anexos e arquivos complementares (designs, imagens, planilhas)
│
├── infra/
│   └── secure_store/ -> Local recomendado para apontamento local/exemplos de credenciais
│                        NOTA: Evite commitar arquivos reais aqui. Armazene somente exemplos
│                        com sufixo `.example`
│
├── airflow-dags/
│   ├── uat/         -> DAGs e configurações específicas do ambiente de UAT
│   └── prod/        -> DAGs e configurações específicas do ambiente de Produção
│
├── dashboards/      -> Artefatos e configurações dos dashboards (Metabase, Grafana, Superset)
│
├── generative-ai/   -> Aplicações, POCs, pipelines e utilitários relacionados a Generative AI
│
└── knowledge-base/  -> Biblioteca de conteúdo (PDFs, livros, documentos, guias, whitepapers)
```

## Boas práticas e regras

### 1. Segredos e credenciais

- NÃO commitar chaves, tokens ou credenciais no repositório.
- Mantenha arquivos de exemplo com sufixo `.example` (ex.: `credentials.example.json`) para documentar a estrutura esperada.
- Use Google Secret Manager, GCS com buckets privados + IAM, ou outro secret manager corporativo.
- Para deploys automatizados, utilize variáveis de ambiente e integração segura de secrets no CI/CD.

### 2. Nome de pastas sensíveis

- A pasta anteriormente chamada de `secret` foi documentada/renomeada para `infra/secure_store` neste README para reduzir exposição direta. Evite nomes óbvios em repositórios públicos e nunca inclua segredos reais.

### 3. Airflow

- Separe as DAGs por ambiente em `airflow-dags/uat` e `airflow-dags/prod`.
- Gerencie conexões e variáveis sensíveis via Airflow Variables/Connections em conjunto com Secret Backends (ex.: GCP Secret Manager).

### 4. Documentação e APIs

- Documente APIs em `apis/` com OpenAPI/Swagger quando aplicável e mantenha documentação técnica em `docs/`.
- Inclua README locais em subpastas explicando como rodar, implantar e testar cada componente.

### 5. Governança das marcas

- Para cada marca criada em `brands/<marca>/`, inclua um README com owner, responsáveis, contatos e instruções específicas de configuração/deployment.

## Exemplo de .gitignore sugerido

```gitignore
# Credenciais
infra/secure_store/*
!infra/secure_store/*.example

# Build / artefatos
dist/
build/

# Arquivos de sistema
.DS_Store
```

## Contribuição e responsáveis

- Mantenedores: @gustavosantosw
- Para alterações na estrutura de pastas, abra uma issue descrevendo a proposta, riscos e motivo da mudança.
- Para inclusão de novos componentes (APIs, DAGs, dashboards), crie uma PR com README e instruções de deploy/rollback.

## Contato

Para dúvidas sobre organização e segurança, contate os responsáveis do projeto.

---

## Changelog

**Versão 1.0.0** - Publicado em 2026-01-16
