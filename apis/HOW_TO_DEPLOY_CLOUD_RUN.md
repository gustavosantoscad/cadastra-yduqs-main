

````
# Deploy da API no Google Cloud Run (Privado / IAM) — Guia Completo

Este documento descreve como fazer deploy da API Python no **Cloud Run** usando **Cloud Build** e **Artifact Registry**, com **acesso privado via IAM** (sem `allow-unauthenticated`) e autenticação via **ID Token (OIDC)**.

> ✅ Padrão adotado: a API usa **ADC (Application Default Credentials)** no Cloud Run via **Service Account do runtime**.  
> ❌ Não usamos JSON de chave dentro do container.

---

## 1) Pré-requisitos

### 1.1 Permissões (IAM) para quem faz o deploy
A conta (seu usuário) que roda os comandos precisa, no mínimo, de:
- Cloud Run Admin
- Artifact Registry Admin/Writer
- Cloud Build Editor/Builder
- Service Account User (para “anexar” a Service Account no serviço do Cloud Run)
- (Opcional) Secret Manager Admin/Accessor

### 1.2 Permissões para a Service Account do Cloud Run (runtime)
A Service Account usada pelo serviço do Cloud Run precisa do que a API faz, por exemplo:
- BigQuery (no dataset/tabelas alvo) — preferencialmente em nível de dataset
- Secret Manager Accessor (se a API ler secrets)

---

## 2) Preparação no Windows (PowerShell)

### 2.1 Instalar e autenticar o Google Cloud CLI
Instale o **Google Cloud CLI** no Windows e depois execute no **PowerShell**:

```powershell
gcloud auth login
gcloud auth application-default login
````

### **2.2 Entrar na pasta do projeto**

Abra o PowerShell e vá até a raiz do projeto (onde está o `Dockerfile`):

```
cd C:\caminho\para\o\repo
dir
```

Você deve ver algo como:

* `Dockerfile`  
* `main.py`  
* `requirements.txt`  
* `controller\`  
* `database\`

---

## **3\) Configuração do projeto no GCP (uma vez)**

### **3.1 Definir projeto e região**

```
gcloud config set project SEU_PROJETO_ID
gcloud config set run/region southamerica-east1
```

### **3.2 Habilitar APIs necessárias**

```
gcloud services enable `
  run.googleapis.com `
  artifactregistry.googleapis.com `
  cloudbuild.googleapis.com `
  iam.googleapis.com `
  secretmanager.googleapis.com
```

### **3.3 Criar repositório no Artifact Registry (uma vez)**

```
gcloud artifacts repositories create api-repo `
  --repository-format=docker `
  --location=southamerica-east1
```

Se já existir, o comando pode falhar com “already exists”. Nesse caso, siga em frente.

---

## **4\) Deploy (modo recomendado: Cloud Build → Cloud Run)**

### **4.1 Variáveis necessárias (copie e edite)**

Defina os valores abaixo no PowerShell:

```
$PROJECT="SEU_PROJETO_ID"
$REGION="southamerica-east1"
$REPO="api-repo"
$SERVICE="googleads-api"
$TAG="1.0.1"

# Service Account do Cloud Run (runtime) — você já tem uma
$SA="SUA_SERVICE_ACCOUNT@$PROJECT.iam.gserviceaccount.com"

# Imagem no Artifact Registry
$IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPO/$SERVICE`:$TAG"
```

**Recomendação forte:** sempre incremente a `TAG` (ex.: `1.0.1`, `1.0.2` ou `20260113-001`).  
Isso dá rastreabilidade e facilita rollback.

---

### **4.2 Build e push com Cloud Build (sem Docker local)**

Rode na raiz do projeto (pasta do Dockerfile):

```
gcloud config set project $PROJECT
gcloud config set run/region $REGION

gcloud builds submit --tag $IMAGE
```

---

### **4.3 Deploy no Cloud Run (Privado / IAM)**

```
gcloud run deploy $SERVICE `
  --image $IMAGE `
  --no-allow-unauthenticated `
  --service-account $SA `
  --port 8080 `
  --region $REGION `
  --set-env-vars ENV=prod
```

✅ Isso cria uma nova **revision** e direciona o tráfego automaticamente para ela.

---

## **5\) Controle de acesso (quem pode invocar o serviço)**

Como o serviço é privado, você precisa conceder `roles/run.invoker` para usuários ou service accounts chamadoras.

### **5.1 Conceder acesso para um usuário (para testes)**

```
gcloud run services add-iam-policy-binding $SERVICE `
  --member="user:seu.email@empresa.com" `
  --role="roles/run.invoker" `
  --region $REGION
```

### **5.2 Conceder acesso para outra Service Account (caller)**

```
gcloud run services add-iam-policy-binding $SERVICE `
  --member="serviceAccount:caller-sa@$PROJECT.iam.gserviceaccount.com" `
  --role="roles/run.invoker" `
  --region $REGION
```

---

## **6\) Testes (PowerShell)**

### **6.1 Obter URL do serviço**

```
$URL = gcloud run services describe $SERVICE --region $REGION --format="value(status.url)"
$URL
```

### **6.2 Healthcheck autenticado**

```
$TOKEN = gcloud auth print-identity-token
Invoke-RestMethod -Headers @{Authorization="Bearer $TOKEN"} -Uri "$URL/health"
```

### **6.3 Executar o job (`POST /run`)**

Edite o `sample_request.json` com os valores do seu ambiente (Google Ads \+ BigQuery).

Campos que você **precisa** ajustar:

* `project_id`  
* `destination_table` (formato `dataset.tabela`)  
* `if_exists` (recomendado: `append`)  
* credenciais Google Ads: `developer_token`, `refresh_token`, `client_id`, `client_secret`, `login_customer_id`, `customer_ids`

Você pode omitir `start_date` e `end_date` para usar o reprocessamento padrão.

Executar:

```
$TOKEN = gcloud auth print-identity-token
$body = Get-Content .\sample_request.json -Raw

Invoke-RestMethod `
  -Method Post `
  -Headers @{Authorization="Bearer $TOKEN"; "Content-Type"="application/json"} `
  -Body $body `
  -Uri "$URL/run"
```

---

## **7\) BigQuery: criação de tabela e dataset**

### **7.1 A tabela é criada automaticamente?**

✅ **Sim**, a tabela pode ser criada automaticamente **se o dataset já existir**, porque o pipeline usa `pandas_gbq.to_gbq()`.

Além disso, o código foi preparado para:

* **não executar `DELETE`** quando a tabela ainda não existe (primeira carga)  
* inserir e deixar o `to_gbq()` criar a tabela

### **7.2 O dataset é criado automaticamente?**

❌ **Não por padrão**. O dataset deve existir previamente.

**Recomendação:** criar dataset via Terraform/IaC (padrão corporativo).

---

## **8\) Atualizações (redeploy após alterações)**

Mudou código? Faça:

1. Incrementar `TAG`  
2. Novo build (`gcloud builds submit`)  
3. Novo deploy (`gcloud run deploy`)

Exemplo:

```
$TAG="1.0.2"
$IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPO/$SERVICE`:$TAG"

gcloud builds submit --tag $IMAGE

gcloud run deploy $SERVICE `
  --image $IMAGE `
  --no-allow-unauthenticated `
  --service-account $SA `
  --port 8080 `
  --region $REGION `
  --set-env-vars ENV=prod
```

---

## **9\) (Opcional) Restringir por rede também (Ingress)**

Além do IAM, você pode bloquear acesso direto da internet.

### **9.1 Somente interno**

```
gcloud run services update $SERVICE --ingress internal --region $REGION
```

### **9.2 Interno \+ via Cloud Load Balancing**

```
gcloud run services update $SERVICE --ingress internal-and-cloud-load-balancing --region $REGION
```

Use isso quando a API deve ser acessada só por tráfego interno/VPC/LB.  
Dependendo do seu cenário, pode exigir arquitetura adicional (LB, Serverless NEG, etc.).

---

## **10\) Verificações úteis**

### **10.1 Ver URL e revision atual**

```
gcloud run services describe $SERVICE --region $REGION --format="value(status.url)"
gcloud run services describe $SERVICE --region $REGION --format="value(status.latestReadyRevisionName)"
```

### **10.2 Logs**

No Console: Cloud Run → Service → Logs  
Ou via CLI:

```
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE" --limit 50
```

---

## **11\) Troubleshooting (direto ao ponto)**

### **11.1 Erro 403 ao chamar a URL**

Causas comuns:

* seu usuário/service account não tem `roles/run.invoker`  
* token inválido (precisa ser ID token/OIDC)

### **11.2 Build falha “Dockerfile not found”**

Você não está na pasta correta. Rode o build na raiz do projeto (onde está o Dockerfile).

### **11.3 BigQuery “Not found: Dataset”**

O dataset não existe. Crie o dataset antes.

### **11.4 Erro de import/módulo no runtime**

Garanta:

* `controller/__init__.py`  
* `database/__init__.py`  
  E imports consistentes com a estrutura do projeto.

---

```

```

