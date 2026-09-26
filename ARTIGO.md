🇧🇷 Português | [🇺🇸 English](ARTIGO.en-us.md)

# Uma falha de rede que se disfarçava de "sem dados"

Esse é, de longe, o repositório mais maduro que produtizei nessa leva — já tinha quatro pipelines de CI (lint, testes, security scan, build+run do container Lambda de verdade), Trivy, testes com mocks bem feitos, um Dockerfile já com um workaround de CVE do urllib3. Não era um projeto abandonado. E ainda assim tinha um bug de um tipo específico: silencioso, e que só aparece quando a rede falha — exatamente quando você mais precisa saber que algo deu errado.

## O bug: erro de rede virava "nenhum dado encontrado"

```python
# original
def fetch_resources_by_year(year, dataset_id="balanco-patrimonial"):
    try:
        response = requests.get(pkg_url)
        response.raise_for_status()
        ...
        yield name, df
        ...
    except Exception as e:
        print(f"Error in fetch_resources_by_year: {e}")
        # a função termina aqui, sem levantar nada
```

Se a API do BNDES estivesse fora do ar, retornasse um 500, ou o DNS falhasse, essa função simplesmente logava o erro e **parava de gerar itens** — sem re-levantar a exceção. Do ponto de vista de quem chama (`lambda_handler`), isso é indistinguível de "não existe balanço pra esse ano":

```python
for name, df in fetch_resources_by_year(year):
    ...
if not all_dfs:
    return {"statusCode": 404, "body": ...}  # "No data found for year {year}"
```

Uma falha real de infraestrutura vira um `404` comum, não um `500`. E o pipeline inteiro documenta explicitamente que alarmes do CloudWatch e notificações do SNS existem pra pegar erros — mas um `404` não é um erro pro CloudWatch, é uma resposta válida da função. Um dia de indisponibilidade da API do BNDES passaria batido, sem alarme, sem nada no SNS, e ninguém saberia que faltou um dia de dados até notar o buraco no S3 semanas depois.

## A correção: deixar o erro subir

```python
def fetch_resources_by_year(year, dataset_id="balanco-patrimonial"):
    ...
    response = requests.get(pkg_url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    ...
    yield name, df
```

Removi o `try/except` que engolia tudo. Agora uma falha de rede propaga até o `try/except` do `lambda_handler`, que já existia e já fazia a coisa certa — devolver `statusCode: 500` com a mensagem do erro. Nenhuma lógica nova, só parar de esconder o sintoma um nível abaixo de onde ele já era tratado corretamente.

De quebra, adicionei `timeout=30` nas duas chamadas `requests.get` (não existia nenhum timeout antes — numa Lambda com 900s de limite, uma conexão pendurada consumiria o orçamento inteiro de execução sem nunca dar erro).

## Um detalhe que só apareceu ao ler com calma: `process_data` sendo chamado e ignorado

```python
for name, df in fetch_resources_by_year(year):
    if not df.empty:
        process_data(df)          # retorno descartado
        all_dfs.append(df)        # usa o df "original"
```

Isso não é um bug — `process_data` faz `df.dropna(inplace=True)`, então a mutação acontece no mesmo objeto que é anexado depois. Funciona por acidente de implementação, não por design. Deixei explícito (`df = process_data(df)`), porque a próxima pessoa que tocar em `process_data` e trocar `inplace=True` por uma cópia vai introduzir silenciosamente o mesmo tipo de bug que acabei de corrigir em `fetch_data.py`.

## O resto: tipos, testes, CI modernizado

Adicionei type hints em tudo (`mypy` limpo), troquei `black`+`flake8` por `ruff` (padrão do resto da organização), fixei as versões do `requests`/`urllib3`/`pyarrow` (tinham CVEs conhecidas, corrigidas na troca), e escrevi testes para os caminhos que faltavam: `save_data` gravando local e no S3, o `ValueError` quando nem bucket nem diretório local estão configurados, o erro de rede se propagando de fato, e o branch de "recurso bate o ano mas o datastore não tem registros". Cobertura foi de ~74% pros 100% dos módulos em `src/`.

Os quatro pipelines existentes (lint, testes, security scan, build+run) continuam fazendo o que já faziam bem — só modernizei as versões das actions, troquei o linter, e adicionei o resto do padrão da organização por cima: dependabot (pip, docker, terraform, github-actions), release semântico, e um scan de dependências agendado. Não toquei no Terraform além de deixar o dependabot vigiar as versões dos providers — o pipeline de infraestrutura já não roda `apply`/`destroy` automaticamente, e não é essa a hora de eu decidir mudar isso.
