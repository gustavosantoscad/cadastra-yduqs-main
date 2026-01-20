# Brands - Recursos Específicos por Marca

Este diretório contém recursos, configurações e artefatos específicos para cada marca do grupo Yduqs. Cada marca possui sua própria subpasta com configurações isoladas, permitindo governança clara e manutenção independente.

## Objetivo

O objetivo desta estrutura é organizar recursos que são específicos de cada marca de forma isolada, facilitando a manutenção, deploy e governança de cada unidade de negócio. Cada marca pode ter suas próprias configurações de API, dashboards customizados, scripts de automação e documentação específica.

## Estrutura

Cada marca possui um diretório dedicado com a seguinte organização sugerida:

**Wyden** (`wyden/`): Recursos e configurações específicas da marca Wyden, incluindo APIs customizadas, dashboards e automações próprias.

**Estácio** (`estacio/`): Configurações e recursos dedicados à marca Estácio, com suas particularidades de negócio e requisitos técnicos.

**Idomed** (`idomed/`): Artefatos relacionados à marca Idomed, incluindo integrações específicas e configurações de sistemas.

**Ibmec** (`ibmec/`): Recursos e configurações da marca Ibmec, contemplando suas necessidades específicas de tecnologia e negócio.

## Governança

Para cada marca, é fundamental manter um README local dentro da subpasta correspondente. Este README deve documentar informações essenciais como owner responsável pela marca, contatos técnicos e de negócio, instruções específicas de configuração e procedimentos de deployment e rollback.

A estrutura interna de cada marca pode variar de acordo com suas necessidades específicas, mas recomenda-se seguir padrões consistentes quando possível, facilitando a navegação e manutenção por diferentes membros da equipe.

## Boas Práticas

Mantenha a separação clara entre recursos compartilhados (que devem estar em outros diretórios do repositório) e recursos específicos de marca. Utilize variáveis de ambiente e configurações externas para facilitar a portabilidade e manutenção do código.

Documente decisões arquiteturais e configurações específicas dentro do README de cada marca. Isso facilita o onboarding de novos membros da equipe e garante continuidade do conhecimento.

Para alterações que impactem múltiplas marcas, considere abstrair o código compartilhado para o diretório apropriado (como `apis/` ou `infra/`), mantendo apenas customizações realmente específicas dentro dos diretórios de marca.
