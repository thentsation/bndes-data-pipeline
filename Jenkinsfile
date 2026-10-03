// Pipeline da plataforma (Shared Library "platform", repo devops-platform/jenkins-lib).
// PRs e branches: validação, CI (docker build --target test), pip-audit e Trivy.
// main: build e smoke test da imagem da Lambda, release (semantic-release), rebuild do
// portfolio e rebuild semanal. Sem deploy: a Lambda vai para a AWS pelo Terraform, à mão.
@Library('platform') _

appPipeline(
    name: 'bndes-data-pipeline',
    deployBranch: 'main',
    deploy: false,
    // PYSEC-2026-113: use-after-free no leitor IPC do Arrow C++ com pre-buffering; o próprio
    // advisory diz que não é alcançável pelos bindings Python. A correção (pyarrow 23.0.1)
    // ainda não tem wheels para o Python 3.11 da Lambda.
    pipAuditIgnore: ['PYSEC-2026-113'],
    // CVE-2026-25087: a mesma falha do PYSEC-2026-113 (pyarrow), vista pelo Trivy na imagem.
    trivyIgnore: ['CVE-2026-25087'],
    notify: [[repo: 'ntsation/portfolio', event: 'rebuild']],
)
