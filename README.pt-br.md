🇧🇷 Português | [🇺🇸 English](README.md)

# Balanço Patrimonial do BNDES - Arquitetura AWS de Produção

Um relato detalhado da produtização deste projeto (uma falha de busca que era engolida em silêncio e reportada como "sem dados" em vez de erro) está em [ARTIGO.md](ARTIGO.md) (pt-br) / [ARTIGO.en-us.md](ARTIGO.en-us.md) (en-us).

Este projeto implementa um sistema pronto para produção que busca, processa e armazena os dados do balanço patrimonial do BNDES na AWS usando tecnologias serverless. O sistema obtém automaticamente os dados da API de Dados Abertos do BNDES, processa-os para garantir consistência e armazena o resultado no S3 como arquivos Parquet particionados por data.

## Desenvolvimento local

```bash
make install        # cria o .venv, instala config/requirements.txt + config/requirements-dev.txt
make test           # pytest, gate de 90% de cobertura
make lint            # ruff check
make typecheck        # mypy
make docker-run        # constrói a imagem da Lambda e a executa localmente contra LOCAL_OUTPUT_DIR
```

O CI roda no Jenkins da plataforma (veja [Pipeline de CI/CD](#pipeline-de-cicd)). `terraform plan`/`apply`/`destroy` continuam sendo ações manuais, disparadas por humanos contra a infraestrutura real da AWS - nada no CI encosta nelas.

## Visão geral

Este projeto oferece acesso automatizado aos dados do Balanço Patrimonial do BNDES, que contém as demonstrações financeiras do banco apresentadas em três padrões:
- **BRGAAP** (Princípios Contábeis Geralmente Aceitos no Brasil)
- **IFRS** (Normas Internacionais de Relatório Financeiro)
- **Conglomerado Prudencial**

O sistema oferece:

- **Ingestão automatizada de dados**: busca automatizada dos dados do balanço patrimonial do BNDES por ano
- **Processamento de dados**: limpeza e consolidação dos dados de vários recursos
- **Monitoramento**: observabilidade completa com logs, métricas, alarmes e dashboards do CloudWatch
- **Alertas**: notificações SNS para falhas e erros críticos
- **Infraestrutura como código**: configuração Terraform completa para deploys reproduzíveis

## Funcionalidades

- **Pipeline de dados automatizado**: execução diária via CloudWatch Events às 03:00 UTC
- **Arquitetura serverless**: Lambda com containers Docker no ECR para facilitar deploy e escala
- **Persistência de dados**: dados processados armazenados no S3 como Parquet com criptografia KMS
- **Monitoramento abrangente**: logs, métricas customizadas, alarmes e dashboards do CloudWatch
- **Sistema de alertas**: notificações SNS para falhas, erros e limites de métricas
- **Tratamento de erros**: Dead Letter Queue (SQS) para execuções da Lambda que falharam
- **Pipeline de CI/CD**: lint, testes, varredura de segurança e build da imagem automatizados no Jenkins da plataforma
- **Segurança**: criptografia KMS, políticas IAM de menor privilégio, state versionado, nenhuma credencial fixa no código
- **Infraestrutura como código**: configuração Terraform completa com arquitetura modular

## Arquitetura

### Arquitetura do sistema

```
┌─────────────┐
│  CloudWatch │
│   Events    │ (Gatilho diário às 03:00 UTC)
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────┐     ┌─────────┐
│   Lambda    │────▶│    S3    │     │   ECR   │
│  Function   │     │  Bucket  │     │   Repo  │
│  (Docker)   │     │(Parquet) │     │         │
│             │     │Partição  │     │         │
│  Busca API  │     │ por data │     │ Imagens │
│  Processa   │     │Cript KMS │     │ Docker  │
│  Envia      │     │          │     │         │
└──────┬──────┘     └──────────┘     └─────────┘
       │
       ▼ (falhas)
┌─────────────┐
│  SQS DLQ    │
│ (Mensagens  │
│  com falha) │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ CloudWatch │────▶│    SNS      │
│ + Alarmes  │     │ (E-mail)    │
│            │     │             │
│  Erros     │     │ Assinaturas │
│  Duração   │     │ de alerta   │
│  Throttles │     │             │
└─────────────┘     └─────────────┘
```

### Fluxo de dados

1. **Gatilho**: o CloudWatch Events dispara a função Lambda diariamente às 03:00 UTC
2. **Busca dos dados**: a Lambda busca os dados na API de Dados Abertos do BNDES
3. **Processamento**: os dados são limpos e consolidados a partir de vários recursos
4. **Armazenamento**: os dados processados são convertidos para Parquet e enviados ao S3
5. **Particionamento**: os arquivos são armazenados com partição por data (ex.: `s3://bucket/2026/01/01/data.parquet`)
6. **Monitoramento**: todas as operações são registradas no CloudWatch Logs
7. **Alertas**: erros disparam alarmes do CloudWatch, que enviam notificações SNS

### Detalhes dos componentes

#### Função Lambda
- **Runtime**: Python 3.11 em container Docker
- **Timeout**: 900 segundos (15 minutos)
- **Memória**: 1024 MB
- **Gatilhos**: CloudWatch Events (expressão cron)
- **Tratamento de erros**: eventos com falha enviados à SQS DLQ para investigação

#### Repositório ECR
- Armazena as imagens Docker da função Lambda
- Varredura de imagens habilitada por segurança
- Políticas de ciclo de vida para gerenciar as imagens

#### Bucket S3
- Armazena os dados processados como arquivos Parquet
- Criptografia KMS em repouso
- Particionamento por data (ano/mês/dia/)
- Versionamento habilitado para recuperação de dados
- Bloqueia todo acesso público

#### CloudWatch
- **Grupo de logs**: armazena os logs de execução da Lambda com retenção de 30 dias
- **Métricas**: métricas customizadas para erros, duração e throttles
- **Alarmes**: alarmes para taxa de erros e limites de duração
- **Dashboard**: visão geral da saúde e do desempenho do sistema

#### Tópico SNS
- Notificações por e-mail para:
  - Falhas de execução da Lambda
  - Taxa de erros acima do limite
  - Duração acima do limite
  - Acúmulo de mensagens na DLQ

#### SQS DLQ
- Recebe as invocações da Lambda que falharam
- Permite investigar as falhas
- Permite reprocessar manualmente os eventos com falha

## Estrutura do projeto

```
bndes-data-pipeline/
├── src/                        # Código-fonte
│   ├── __init__.py
│   ├── app.py                  # Entrypoint da Lambda com a lógica de upload para o S3
│   ├── fetch_data.py           # Módulo de busca de dados na API do BNDES
│   └── process_data.py         # Módulo de processamento e transformação de dados
├── docker/Dockerfile           # Imagem da Lambda + stages de CI (target test)
├── config/                     # requirements.txt, requirements-dev.txt, requirements.lock
├── Jenkinsfile                 # Pipeline da plataforma (appPipeline)
├── data/                       # Diretório local de dados (no .gitignore)
│   └── bndes-data/
│       └── 2026/
│           └── 01/
│               └── 01/
├── notebooks/                  # Notebooks Jupyter para análise
│   └── bndes_analysis.ipynb    # Análise e visualização dos dados
├── terraform/                  # Infraestrutura como código
│   ├── main.tf                 # Configuração principal do Terraform
│   ├── providers.tf            # Configuração de provider e backend
│   ├── variables.tf            # Variáveis de entrada
│   ├── outputs.tf              # Valores de saída
│   ├── terraform.tfvars        # Valores das variáveis
│   ├── .gitignore              # Arquivos de state do Terraform
│   └── modules/                # Módulos Terraform reutilizáveis
│       ├── ecr/                # Módulo do repositório ECR
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── lambda/             # Módulo da função Lambda
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── s3/                 # Módulo do bucket S3
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── monitoring/         # Módulo CloudWatch + SNS
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       └── schedule/           # Módulo CloudWatch Events
│           ├── main.tf
│           ├── variables.tf
│           └── outputs.tf
├── tests/                      # Testes unitários
│   ├── __init__.py
│   ├── test_app.py
│   ├── test_fetch_data.py
│   └── test_process_data.py
├── scripts/                    # Scripts utilitários
│   └── setup-terraform-backend.sh
├── docker-compose.yml         # Docker Compose para desenvolvimento local
├── README.md                   # README em inglês
├── README.pt-br.md             # Este arquivo
└── .gitignore                  # Padrões ignorados pelo Git
```

## Processamento de dados

### Fonte de dados

O sistema busca dados no dataset "balanco-patrimonial" da API de Dados Abertos do BNDES, que contém o Balanço Patrimonial do BNDES apresentado em três padrões contábeis:
- **BRGAAP** (Princípios Contábeis Geralmente Aceitos no Brasil)
- **IFRS** (Normas Internacionais de Relatório Financeiro)
- **Conglomerado Prudencial**

Os dados incluem informações financeiras como:
- Descrições e classificações das contas
- Valores e saldos financeiros
- Informações de período
- Métricas específicas de cada padrão

### Transformação dos dados

O módulo `process_data.py` faz a limpeza e a preparação dos dados:

1. **Limpeza**: remove linhas vazias e limpa campos de texto (ex.: remove espaços das descrições)
2. **Consolidação**: combina vários recursos (ex.: diferentes padrões contábeis) em um único dataset consolidado
3. **Metadados**: adiciona o nome e o ID do recurso de origem para rastreabilidade
4. **Validação**: garante a integridade dos dados antes do armazenamento

### Formato de saída

Os dados processados são armazenados em Parquet, com os seguintes benefícios:
- Armazenamento colunar para consultas eficientes
- Compressão para reduzir o custo de armazenamento
- Suporte a evolução de schema
- Particionamento por data para consultas otimizadas

## Início rápido

### Pré-requisitos

Antes de começar, garanta que você tem:

- **Conta AWS** com as permissões adequadas (Lambda, S3, CloudWatch, ECR, SQS, SNS, KMS, IAM)
- **AWS CLI** instalado e configurado com credenciais
- **Docker** instalado (para construir as imagens da Lambda)
- **Terraform** >= 1.5.0 instalado
- **Python 3.11** instalado
- **Conta no GitHub** (para CI/CD)
- **jq** (opcional, para ler os outputs do Terraform)

### 1. Clonar o repositório

```bash
git clone https://github.com/your-username/bndes-data-pipeline.git
cd bndes-data-pipeline
```

### 2. Instalar as dependências Python

```bash
pip install -r config/requirements.txt
```

### 3. Configurar o backend do Terraform

O state do Terraform fica no S3 para persistência e colaboração. Rode o script de setup para criar os recursos AWS necessários:

```bash
chmod +x scripts/setup-terraform-backend.sh
./scripts/setup-terraform-backend.sh
```

Este script vai:
- Criar um bucket S3 para o state do Terraform
- Criar uma tabela DynamoDB para o lock do state
- Habilitar versionamento e criptografia

### 4. Configurar as variáveis

Edite `terraform/terraform.tfvars` com os valores desejados:

```hcl
aws_region          = "us-east-1"
project_name        = "bndes-data-pipeline"
lambda_timeout      = 900
lambda_memory_size  = 1024
alarm_email         = "your-email@example.com"
log_retention_days  = 30
```

### 5. Fazer o deploy da infraestrutura

Faça o deploy da infraestrutura AWS com o Terraform:

```bash
cd terraform
terraform init
terraform plan  # Revise as mudanças
terraform apply # Faz o deploy da infraestrutura
```

### 6. Construir e enviar a imagem Docker

Construa a imagem Docker e envie ao ECR:

```bash
# Obter a URI do repositório ECR
ECR_URI=$(terraform output ecr_repository_url)
REGION=$(terraform output aws_region)

# Login no ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

# Construir a imagem
docker build --target runtime -f docker/Dockerfile -t bndes-data-pipeline:latest .

# Taguear a imagem
docker tag bndes-data-pipeline:latest $ECR_URI:latest

# Enviar a imagem
docker push $ECR_URI:latest
```

### 7. Atualizar a função Lambda

Atualize a função Lambda para usar a nova imagem Docker:

```bash
# Ir para o diretório terraform
cd terraform

# Atualizar a função Lambda
terraform apply -var="docker_image_tag=latest"
```

### 8. Verificar o deploy

Confira se o deploy deu certo:

```bash
# Ver os outputs do Terraform
terraform output

# Outputs esperados:
# - ecr_repository_url
# - lambda_function_name
# - lambda_function_arn
# - s3_bucket_name
# - log_group_name
# - dashboard_url
```

### 9. Testar o pipeline

Dispare a função Lambda manualmente para testar o pipeline de dados:

```bash
# Obter o nome da função Lambda
FUNCTION_NAME=$(terraform output lambda_function_name)

# Invocar a função Lambda
aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload '{}' \
  --cli-binary-format raw-in-base64-out \
  response.json

# Ver a resposta
cat response.json

# Ver os logs
LOG_GROUP=$(terraform output log_group_name)
aws logs tail $LOG_GROUP --follow
```

## Configuração

### Variáveis do Terraform

Principais variáveis de configuração em `terraform/main.tf`:

| Variável | Tipo | Padrão | Descrição |
|-----------|------|---------|-------------|
| `aws_region` | string | `us-east-1` | Região AWS do deploy |
| `project_name` | string | `bndes-data-pipeline` | Prefixo de todos os recursos AWS |
| `lambda_timeout` | number | `900` | Timeout da função Lambda em segundos (máx. 900) |
| `lambda_memory_size` | number | `1024` | Memória da função Lambda em MB (128-10288) |
| `alarm_email` | string | `""` | E-mail para as notificações SNS |
| `log_retention_days` | number | `30` | Retenção dos logs do CloudWatch em dias |

### Variáveis de ambiente

A função Lambda usa estas variáveis de ambiente:

| Variável | Descrição | Obrigatória |
|-----------|-------------|----------|
| `S3_BUCKET_NAME` | Nome do bucket S3 para armazenar os dados | Sim |
| `LOCAL_OUTPUT_DIR` | Diretório local para processamento dos dados | Sim |
| `BNDES_API_URL` | Endpoint da API do BNDES | Sim |

## Monitoramento

### Dashboard do CloudWatch

Acesse o dashboard de monitoramento:

```bash
# Obter a URL do dashboard
terraform output dashboard_url
```

Ou navegue manualmente no Console AWS:
1. Abra o Console do CloudWatch
2. Vá em Dashboards
3. Selecione `bndes-data-pipeline-dashboard`

O dashboard mostra:
- Métricas de invocação da Lambda (invocações, erros, duração, throttles)
- Métricas de armazenamento do S3
- CloudWatch Logs Insights
- Status recente dos alarmes

### Ver os logs

Acompanhe os logs de execução da Lambda em tempo real:

```bash
# Obter o nome do grupo de logs
LOG_GROUP=$(terraform output log_group_name)

# Acompanhar os logs
aws logs tail $LOG_GROUP --follow
```

### Verificar alarmes

Liste todos os alarmes associados ao projeto:

```bash
aws cloudwatch describe-alarms --alarm-name-prefix bndes-data-pipeline
```

### Métricas customizadas

O sistema acompanha estas métricas customizadas:
- **Errors**: erros de execução da Lambda
- **Duration**: duração da execução da Lambda
- **Throttles**: eventos de throttling da Lambda
- **Invocations**: total de invocações da Lambda
- **Successes**: execuções da Lambda bem-sucedidas

## Pipeline de CI/CD

CI e deploy rodam no Jenkins da plataforma (`Jenkinsfile` → `appPipeline` da Shared Library `platform`, repo devops-platform), disparados por webhooks. Sem GitHub Actions.

- **PRs e branches** — validação do contrato; `docker build --target test` (`ruff check`, `ruff format --check`, `mypy`, `pytest` com cobertura ≥90%, versões das ferramentas no `config/requirements-dev.txt`); `pip-audit` no `config/requirements.lock`; Trivy (CRITICAL/HIGH) na imagem da Lambda; vulnerabilidades aceitas, se houver, ficam listadas com a justificativa no `Jenkinsfile`.
- **main** — tudo acima e depois build e smoke test da imagem da Lambda, release com o python-semantic-release (versão, CHANGELOG, tag e release no GitHub) e rebuild do portfolio. Também é reconstruída toda segunda para pegar patches de segurança. Nada é enviado para a AWS: a imagem vai para o ECR e a infraestrutura para a AWS só pelo `terraform apply`, rodado por um humano.
- **Dependências** — Renovate (job `platform/renovate` no Jenkins, `renovate.json` → preset do devops-platform): atualizações diárias, manutenção semanal do lockfile, issue "Dependency Dashboard" e auto-merge de patch/minor depois que o Jenkins aprova.

## Desenvolvimento local (detalhado)

### Rodando os testes

Rode os testes unitários localmente:

```bash
# Incluir o diretório src no PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Rodar todos os testes
pytest tests/ -v

# Rodar com cobertura
pytest tests/ --cov=src --cov-report=html

# Rodar um arquivo de teste específico
pytest tests/test_fetch_data.py -v
```

### Construindo a imagem Docker

Construa a imagem Docker localmente para testar:

```bash
# Construir a imagem
docker build --target runtime -f docker/Dockerfile -t bndes-data-pipeline:latest .

# Rodar o container
docker run -p 9000:8080 \
  -e S3_BUCKET_NAME="test-bucket" \
  -e LOCAL_OUTPUT_DIR="/tmp/local_data" \
  bndes-data-pipeline:latest
```

### Rodando localmente (simulação)

Simule a execução da Lambda localmente:

```bash
# Definir as variáveis de ambiente
export S3_BUCKET_NAME="test-bucket"
export LOCAL_OUTPUT_DIR="./data"

# Rodar a função principal
python src/app.py
```

### Usando notebooks Jupyter

Abra o notebook de análise para explorar os dados:

```bash
# Instalar o Jupyter
pip install jupyter notebook

# Iniciar o Jupyter
jupyter notebook

# Abrir notebooks/bndes_analysis.ipynb
```

### Desenvolvimento local com Terraform

Teste mudanças no Terraform localmente sem afetar a produção:

```bash
cd terraform

# Inicializar com backend local (sem S3)
terraform init -backend=false

# Validar a configuração
terraform validate

# Gerar o plano
terraform plan

# Formatar o código
terraform fmt -recursive
```

## Estimativa de custo

Custos mensais (us-east-1) com uso típico:

| Serviço | Custo estimado | Observações |
|---------|----------------|-------|
| Lambda | ~US$ 0,20 | 1 invocação/dia, 900 s de duração, 1024 MB |
| ECR | ~US$ 0,10 | Armazenamento das imagens Docker |
| S3 | ~US$ 0,05 | 1 GB/mês de arquivos Parquet |
| CloudWatch Logs | ~US$ 0,10 | 1 GB/mês de ingestão de logs |
| SQS DLQ | ~US$ 0,00 | Pago por uso (mínimo) |
| SNS | ~US$ 0,00 | 1000 e-mails grátis/mês |
| KMS | ~US$ 0,03 | Uso da chave KMS |
| CloudWatch Metrics | ~US$ 0,00 | Métricas customizadas dentro do free tier |
| **Total** | **~US$ 0,48/mês** |  |

**Observação**: os custos podem variar conforme o uso real, o volume de dados e mudanças de preço da AWS.

## Recursos de segurança

O projeto aplica várias boas práticas de segurança:

### Segurança dos dados
- **Criptografia KMS**: todos os dados no S3 criptografados em repouso com AWS KMS
- **Criptografia em trânsito**: todas as transferências usam HTTPS/TLS
- **Nenhuma credencial fixa no código**: nenhum segredo no código ou em arquivos de configuração

### Segurança de IAM
- **Menor privilégio**: a role de execução da Lambda tem só as permissões mínimas necessárias
- **Políticas baseadas em recurso**: as políticas do bucket S3 restringem o acesso a roles específicas
- **Separação de roles**: roles diferentes para funções diferentes (quando aplicável)

### Segurança da infraestrutura
- **S3 Block Public Access**: o bucket bloqueia todo acesso público
- **Varredura de imagens no ECR**: varredura automática de vulnerabilidades a cada push de imagem
- **Isolamento em VPC**: a Lambda pode ser configurada em uma VPC (melhoria futura)

### Segurança do state do Terraform
- **Criptografia do state**: state do Terraform criptografado no S3
- **Versionamento do state**: versionamento do S3 habilitado para recuperar o state
- **Lock do state**: tabela DynamoDB impede modificações concorrentes

### Segurança operacional
- **Logs de auditoria**: o CloudWatch registra todas as execuções da Lambda
- **Alertas de erro**: notificações SNS para erros relevantes de segurança
- **Gestão de segredos**: segredos armazenados nas credenciais do Jenkins e no AWS Secrets Manager

## Solução de problemas

### Timeout da Lambda

**Sintomas**: a função Lambda estoura o tempo antes de terminar.

**Soluções**:
1. Aumente `lambda_timeout` nas variáveis do Terraform (máx. 900 s)
2. Aumente `lambda_memory_size` (mais CPU)
3. Otimize o código de processamento de dados
4. Verifique o tempo de resposta da API do BNDES
5. Adicione paginação para datasets grandes

```bash
cd terraform
terraform apply -var="lambda_timeout=900" -var="lambda_memory_size=2048"
```

### Erros de permissão no S3

**Sintomas**: a Lambda não consegue enviar arquivos ao S3.

**Soluções**:
1. Verifique se as políticas IAM incluem as permissões de S3
2. Confira se a role de execução da Lambda tem a permissão `s3:PutObject`
3. Garanta que a política do bucket S3 permite a role da Lambda
4. Verifique as permissões da chave KMS se estiver usando SSE-KMS

```bash
# Verificar a role da Lambda
aws iam get-role-policy --role-name <lambda-role-name> --policy-name <policy-name>

# Verificar a política do bucket S3
aws s3api get-bucket-policy --bucket <bucket-name>
```

### Erros de falta de memória

**Sintomas**: a Lambda falha com o erro "Memory limit exceeded".

**Soluções**:
1. Aumente `lambda_memory_size` no Terraform
2. Otimize o uso de memória no código
3. Processe os dados em lotes em vez de carregar tudo de uma vez

```bash
cd terraform
terraform apply -var="lambda_memory_size=2048"
```

### Lock do state do Terraform

**Sintomas**: `terraform apply` falha com erro de lock do state.

**Solução**: destrave o state (só se for seguro):

```bash
cd terraform
terraform force-unlock <LOCK_ID>

# Para obter o LOCK_ID:
terraform plan  # A mensagem de erro mostra o Lock ID
```

### Erros na API do BNDES

**Sintomas**: a Lambda não consegue buscar dados na API do BNDES.

**Soluções**:
1. Verifique a URL do endpoint da API nas variáveis de ambiente
2. Confirme que a API do BNDES está acessível
3. Verifique limites de requisição ou mudanças na API
4. Analise a resposta da API nos logs do CloudWatch

### Mensagens acumulando na DLQ

**Sintomas**: mensagens acumulando na SQS DLQ.

**Soluções**:
1. Verifique os logs do CloudWatch em busca de erros da Lambda
2. Investigue as invocações da Lambda que falharam
3. Reprocesse manualmente as mensagens da DLQ depois de corrigir os problemas
4. Ajuste timeout/memória da Lambda se necessário

```bash
# Ver as mensagens da DLQ
aws sqs receive-message --queue-url <dlq-url>

# Reprocessar a mensagem (depois de corrigir os problemas)
# Copie o corpo da mensagem e invoque a Lambda manualmente
```

## Documentação

### Recursos externos

- [Documentação do provider AWS do Terraform](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Documentação do AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Documentação do AWS S3](https://docs.aws.amazon.com/s3/)
- [Documentação do CloudWatch](https://docs.aws.amazon.com/cloudwatch/)
- [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/)
- [Documentação do Docker](https://docs.docker.com/)

### Documentação interna

- `terraform/PIPELINE_SETUP.md`: detalhes da configuração do pipeline Terraform
- `docs/medium-article-terraform-pipeline.md`: artigo sobre a estratégia de backend do Terraform

## Contribuindo

Contribuições são bem-vindas! Siga estas orientações:

1. **Faça um fork do repositório**
   ```bash
   git clone https://github.com/your-username/bndes-data-pipeline.git
   ```

2. **Crie uma branch de feature**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Faça as mudanças**
   - Escreva código limpo e legível
   - Adicione testes para as novas funcionalidades
   - Atualize a documentação quando necessário

4. **Rode os testes localmente**
   ```bash
   pytest tests/ -v
   ```

5. **Faça o commit das mudanças**
   ```bash
   git commit -m 'Add amazing feature: description'
   ```

6. **Envie para a branch**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Abra um Pull Request**
   - Descreva as mudanças com clareza
   - Referencie as issues relacionadas
   - Garanta que todos os checks de CI passam

### Estilo de código

- Siga as diretrizes da PEP 8 para código Python
- Use o Black para formatar o código
- Use nomes descritivos para variáveis e funções
- Adicione docstrings em funções complexas
- Mantenha as funções pequenas e focadas

### Testes

- Escreva testes unitários para as novas funcionalidades
- Busque mais de 80% de cobertura de código
- Teste os casos de sucesso e de erro
- Use mocks para dependências externas nos testes

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para detalhes.

## Suporte

Para problemas, dúvidas ou contribuições:

1. **Abra uma issue**: reporte bugs ou peça funcionalidades no GitHub Issues
2. **Verifique os logs do CloudWatch**: analise os logs de execução da Lambda em busca de erros
3. **Revise o state do Terraform**: use `terraform show` para inspecionar o estado atual
4. **Consulte a documentação**: veja este README e os demais arquivos de documentação

### Comandos úteis

```bash
# Ver o state do Terraform
terraform show

# Ver um recurso específico
terraform show aws_lambda_function.main

# Ver a versão do Terraform
terraform version

# Validar a configuração do Terraform
terraform validate

# Formatar o código Terraform
terraform fmt -recursive

# Ver os logs do CloudWatch
aws logs tail /aws/lambda/bndes-data-pipeline --follow

# Descrever a função Lambda
aws lambda get-function --function-name bndes-data-pipeline

# Listar os objetos do S3
aws s3 ls s3://bndes-data-pipeline-data --recursive
```

## Agradecimentos

- Ao BNDES (Banco Nacional de Desenvolvimento Econômico e Social) por disponibilizar a API de Dados Abertos
- À AWS pela plataforma e pelas ferramentas serverless
- À comunidade Terraform pelas boas práticas de infraestrutura como código

---

**Construído com tecnologias serverless da AWS**

Para mais informações, visite o [repositório do projeto](https://github.com/your-username/bndes-data-pipeline).
