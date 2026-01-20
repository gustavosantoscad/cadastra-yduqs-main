

# 

# DICIONÁRIO TÉCNICO

| Organização:  | Por categorias temáticas |
| :---- | :---- |
| Termos:  | Mais de 150 conceitos técnicos |
| Foco:  | Data Lake, Apache Spark, Databricks |
| Versão:  | January 2026 |

Sobre Este Dicionário  
Este dicionário técnico foi desenvolvido para apoiar engenheiros e analistas de dados no trabalho com Delta Lake, Apache Spark e tecnologias relacionadas. Os termos estão organizados por categorias temáticas para facilitar a consulta durante o desenvolvimento de aplicações e pipelines de dados.

## Categorias Incluídas

* 🔷 Fundamentos Delta Lake \- Conceitos base e arquitetura  
* 🔒 Transações e ACID \- Garantias e controle de concorrência  
* ⚙️ Operações de Dados \- CRUD, MERGE, VACUUM  
* 📊 Streaming e Tempo Real \- Processamento contínuo  
* ⚡ Otimização e Performance \- Tuning e índices  
* 🏗️ Arquitetura Lakehouse \- Medallion e design patterns  
* 🔌 Integrações e Conectores \- Spark, Flink, Trino  
* ✅ Governança e Qualidade \- Schema, constraints, metadata

## Como Usar

Cada termo inclui: tradução em português brasileiro, definição técnica detalhada e contexto de uso no ecossistema Delta Lake. Termos técnicos consolidados são mantidos em inglês quando apropriado, seguindo as melhores práticas da indústria.

# 🔷 Fundamentos Delta Lake

Delta Lake

Tradução: Delta Lake (mantém-se)

Camada de armazenamento open source que traz transações ACID, manipulação escalável de metadados e unificação de processamento de dados em streaming e batch para data lakes.

Data Lakehouse

Tradução: Data Lakehouse / Lakehouse de Dados

Arquitetura que combina os melhores elementos de data lakes e data warehouses. Delta Lake é uma implementação líder desta arquitetura.

Transaction Log

Tradução: Log de Transações

Registro ordenado de todas as transações executadas em uma tabela Delta Lake, armazenado no diretório \_delta\_log.

Parquet

Tradução: Parquet (mantém-se)

Formato de arquivo colunar de código aberto otimizado para uso com frameworks de processamento de big data.

Metadata

Tradução: Metadados

Dados que descrevem outros dados. No Delta Lake, existem informações sobre estrutura de tabelas, esquemas, partições e estatísticas.

# 🔒 Transações e ACID

ACID

Tradução: ACID (mantém-se o acrônimo)

Atomicity, Consistency, Isolation, Durability. Conjunto de propriedades que garantem a confiabilidade das transações.

Atomicity

Tradução: Atomicidade

Propriedade que garante que uma transação seja executada completamente ou não seja executada.

Consistency

Tradução: Consistência

Propriedade ACID que garante que uma transação leve o banco de dados de um estado válido para outro estado válido.

Isolation

Tradução: Isolamento

Propriedade ACID que garante que transações concorrentes sejam executadas isoladamente umas das outras.

Commit

Tradução: Confirmação / Commit

Operação que finaliza uma transação, tornando as mudanças permanentes e visíveis para outros leitores.

# ⚙️ Operações de Dados

MERGE

Tradução: MERGE (comando SQL, mantém-se)

Operação SQL que combina INSERT, UPDATE e DELETE em uma única transação atômica.

OPTIMIZE

Tradução: OPTIMIZE (comando, mantém-se)

Comando Delta Lake que compacta arquivos pequenos em arquivos maiores para melhorar o desempenho de leitura.

VACUUM

Tradução: VACUUM (comando, mantém-se)

Comando Delta Lake que remove arquivos de dados antigos que não são mais referenciados pelo log de transações.

Upsert

Tradução: Upsert (mantém-se)

Operação que insere uma nova linha se não existir ou atualiza se já existir.

# 📊 Streaming e Tempo Real

Structured Streaming

Tradução: Structured Streaming (nome da API, mantém-se)

API de processamento de stream do Apache Spark construída sobre o Spark SQL.

Change Data Feed (CDF)

Tradução: Feed de Dados de Mudança

Funcionalidade do Delta Lake que rastreia mudanças em nível de linha entre versões de tabelas.

Exactly-Once Semantics

Tradução: Semântica Exatamente-Uma-Vez

Garantia de que cada registro é processado exatamente uma vez, sem duplicação ou perda.

# ⚡ Otimização e Performance

Z-Ordering

Tradução: Ordenação Z / Z-Ordering

Técnica de otimização que organiza dados multidimensionalmente usando curva Z.

Data Skipping

Tradução: Salto de Dados

Técnica de otimização que usa estatísticas de metadados para evitar leitura de arquivos irrelevantes.

Bloom Filter Index

Tradução: Índice de Filtro Bloom

Estrutura de dados probabilística usada para testar se um elemento é membro de um conjunto.

# 🏗️ Arquitetura Lakehouse

Medallion Architecture

Tradução: Arquitetura Medallion

Padrão de design de dados que organiza dados em camadas (Bronze, Silver, Gold) com qualidade progressiva.

Bronze Layer

Tradução: Camada Bronze

Primeira camada da arquitetura Medallion onde dados brutos são ingeridos sem transformações significativas.

Silver Layer

Tradução: Camada Silver / Prata

Camada intermediária contendo dados limpos, validados, enriquecidos e deduplicados.

Gold Layer

Tradução: Camada Gold / Ouro

Camada final contendo dados refinados, agregados e prontos para consumo por aplicações de negócios.

# 🔌 Integrações e Conectores

Apache Spark

Tradução: Apache Spark (mantém-se)

Motor de processamento de dados distribuído e de código aberto. Plataforma principal para trabalhar com Delta Lake.

Databricks

Tradução: Databricks (mantém-se)

Plataforma unificada de análise de dados baseada em Apache Spark, com suporte nativo ao Delta Lake.

Delta Sharing

Tradução: Delta Sharing (mantém-se)

Protocolo aberto para compartilhamento seguro de dados em tempo real entre organizações.

# ✅ Governança e Qualidade

Schema Enforcement

Tradução: Imposição de Esquema

Mecanismo que garante que dados escritos em tabela Delta Lake correspondam ao esquema definido.

Schema Evolution

Tradução: Evolução de Esquema

Capacidade de modificar esquema de uma tabela sem reescrever dados existentes.

Time Travel

Tradução: Viagem no Tempo / Time Travel

Capacidade de consultar versões históricas de uma tabela Delta Lake usando timestamps ou números de versão.

