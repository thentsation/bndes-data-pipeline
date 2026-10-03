// Pipeline da plataforma (Shared Library "platform", repo devops-platform/jenkins-lib).
// PRs e branches: validação, CI (docker build --target test), pip-audit e Trivy.
// main: build e smoke test da imagem da Lambda, release (semantic-release), rebuild do
// portfolio e rebuild semanal. Sem deploy: a Lambda vai para a AWS pelo Terraform, à mão.
@Library('platform') _

appPipeline(
    name: 'bndes-data-pipeline',
    deployBranch: 'main',
    deploy: false,
    notify: [[repo: 'ntsation/portfolio', event: 'rebuild']],
)
