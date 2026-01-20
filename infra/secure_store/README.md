# Secure Store - Templates de Configuração

Este diretório contém exclusivamente templates e exemplos de arquivos de configuração. Nenhum arquivo com credenciais, chaves ou tokens reais deve ser armazenado aqui ou commitado no repositório.

## Propósito

O objetivo deste espaço é fornecer estruturas de referência para arquivos de configuração que desenvolvedores precisam criar localmente. Estes exemplos documentam formatos esperados, campos obrigatórios e estruturas de dados sem expor informações sensíveis.

## Convenção de Nomenclatura

Todos os arquivos neste diretório devem utilizar o sufixo `.example` antes da extensão final. Por exemplo, um arquivo de service account do Google Cloud deve ser nomeado `service-account.example.json`, enquanto um arquivo de configuração de API seria `api-config.example.yaml`.

Esta convenção deixa explícito que são templates, não credenciais reais, e permite que o `.gitignore` bloqueie commit acidental de arquivos sem o sufixo `.example`.

## Como Utilizar

Para usar os templates, copie o arquivo de exemplo removendo o sufixo `.example` e preencha com suas credenciais reais. Por exemplo, copie `service-account.example.json` para `service-account.json` e substitua os valores placeholder pelas credenciais obtidas do Google Cloud Console.

Nunca commite o arquivo sem sufixo `.example`. O `.gitignore` está configurado para bloquear estes arquivos, mas desenvolvedores devem sempre validar antes de commitar qualquer mudança neste diretório.

## Credenciais Reais

Armazene credenciais reais em Google Secret Manager ou serviço equivalente. Para desenvolvimento local, mantenha arquivos de credenciais apenas em seu ambiente local, referenciados via variáveis de ambiente que não são versionadas.

Configure sua aplicação para buscar credenciais de variáveis de ambiente ou Secret Manager em runtime, evitando necessidade de armazenar arquivos sensíveis no sistema de arquivos.

## Segurança

Revise periodicamente este diretório para garantir que nenhum arquivo sem sufixo `.example` foi commitado acidentalmente. Utilize hooks de git ou ferramentas de análise de segurança para detectar commits acidentais de credenciais antes que atinjam o repositório remoto.

Em caso de commit acidental de credenciais, rotacione imediatamente todos os secrets expostos e considere reescrever histórico do git para remover informações sensíveis. Notifique equipes de segurança conforme procedimentos estabelecidos.
