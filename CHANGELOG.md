# CHANGELOG

<!-- version list -->

## v1.0.12 (2026-10-10)

### Bug Fixes

- **security**: Ignora CVEs do Go stdlib no aws-lambda-rie da imagem base
  ([#45](https://github.com/thentsation/bndes-data-pipeline/pull/45),
  [`2e8bee8`](https://github.com/thentsation/bndes-data-pipeline/commit/2e8bee83d4a167145db2860930bcf8c9dcc18599))

### Chores

- **deps**: Update boto3 requirement in /config
  ([#44](https://github.com/thentsation/bndes-data-pipeline/pull/44),
  [`d3537fd`](https://github.com/thentsation/bndes-data-pipeline/commit/d3537fda106e5929d2fd61055ce4e0f075c9e471))


## v1.0.11 (2026-10-07)

### Bug Fixes

- **ci**: Scan usa docker/Dockerfile
  ([`34bf861`](https://github.com/thentsation/bndes-data-pipeline/commit/34bf861f7d3267a70332364138b8133972a41a2c))

### Chores

- **deps**: Update dependency types-requests to v2.33.0.20261006
  ([#42](https://github.com/thentsation/bndes-data-pipeline/pull/42),
  [`beb2d9d`](https://github.com/thentsation/bndes-data-pipeline/commit/beb2d9d36e5ef580fe09b7ad944a4a3b8cae88db))

### Documentation

- README pt-br com a Lambda em Python 3.14
  ([#41](https://github.com/thentsation/bndes-data-pipeline/pull/41),
  [`cc55969`](https://github.com/thentsation/bndes-data-pipeline/commit/cc55969b31ee96eeac52f83715fb9d182e167275))


## v1.0.10 (2026-10-03)

### Bug Fixes

- **deps**: Lambda em Python 3.14 com pyarrow 25, numpy 2.5 e pandas 3
  ([#40](https://github.com/thentsation/bndes-data-pipeline/pull/40),
  [`1198a9a`](https://github.com/thentsation/bndes-data-pipeline/commit/1198a9acd555abc671ecf44b35c381b7e0663571))

### Chores

- Isolate lambda handler test output and add pt-br README (T-0012)
  ([#28](https://github.com/thentsation/bndes-data-pipeline/pull/28),
  [`243fb4c`](https://github.com/thentsation/bndes-data-pipeline/commit/243fb4c87a70d5aeb02d8fad230d19ff76289be6))

- **deps**: Update dependency boto3-stubs to v1.43.108
  ([#33](https://github.com/thentsation/bndes-data-pipeline/pull/33),
  [`cc06f44`](https://github.com/thentsation/bndes-data-pipeline/commit/cc06f442b53f0c1a90f149ec96152dd24926aa64))

- **deps**: Update dependency mypy to v2.4.0
  ([#35](https://github.com/thentsation/bndes-data-pipeline/pull/35),
  [`97cc1cb`](https://github.com/thentsation/bndes-data-pipeline/commit/97cc1cb185595831c08652c391329087a7e76b18))

- **deps**: Update dependency ruff to v0.16.10
  ([#34](https://github.com/thentsation/bndes-data-pipeline/pull/34),
  [`97f9e3e`](https://github.com/thentsation/bndes-data-pipeline/commit/97f9e3e6eb65bc171fa022955144b352dc329782))

### Continuous Integration

- Pipeline da Shared Library da plataforma e Renovate
  ([#31](https://github.com/thentsation/bndes-data-pipeline/pull/31),
  [`81b1d32`](https://github.com/thentsation/bndes-data-pipeline/commit/81b1d325b298ee2c75b6f7c3beebd4cb552e4b6c))

### Documentation

- README pt-br no padrão da plataforma (Jenkins, config/, docker/)
  ([#28](https://github.com/thentsation/bndes-data-pipeline/pull/28),
  [`243fb4c`](https://github.com/thentsation/bndes-data-pipeline/commit/243fb4c87a70d5aeb02d8fad230d19ff76289be6))


## v1.0.9 (2026-09-28)

### Bug Fixes

- **ci**: Open lockfile PRs with RELEASE_PAT so CI runs on them
  ([`cacf3a5`](https://github.com/thentsation/bndes-data-pipeline/commit/cacf3a5292bc07ed692d65ea5ab382c4e43b869b))

### Chores

- **deps**: Bump boto3-stubs from 1.43.100 to 1.43.102
  ([#19](https://github.com/thentsation/bndes-data-pipeline/pull/19),
  [`1e721fa`](https://github.com/thentsation/bndes-data-pipeline/commit/1e721fa02357cf908411ed93148911ce58a7e8ea))

- **deps**: Bump ruff from 0.16.8 to 0.16.9
  ([#21](https://github.com/thentsation/bndes-data-pipeline/pull/21),
  [`97f399f`](https://github.com/thentsation/bndes-data-pipeline/commit/97f399fb9ae2ff9d33c435286f61a6624b8d2b4e))

- **deps**: Ignore pandas 3 and pyarrow 21+ majors in dependabot
  ([`8af6beb`](https://github.com/thentsation/bndes-data-pipeline/commit/8af6beb185efb39b94132bf88844a43061f66f55))

- **deps**: Update boto3 requirement
  ([#18](https://github.com/thentsation/bndes-data-pipeline/pull/18),
  [`b26e683`](https://github.com/thentsation/bndes-data-pipeline/commit/b26e683e3c23c3187ddcf98bbd65e392d27a7c7e))

- **deps**: Update numpy requirement from <2.3,>=1.26 to >=2.2.6,<2.3
  ([#23](https://github.com/thentsation/bndes-data-pipeline/pull/23),
  [`c8ae6f7`](https://github.com/thentsation/bndes-data-pipeline/commit/c8ae6f73cf3969fa79a775ffa8494244e880ce33))

- **deps**: Update pandas requirement from <2.4,>=2.3 to >=2.3.3,<2.4
  ([#20](https://github.com/thentsation/bndes-data-pipeline/pull/20),
  [`da3cc1b`](https://github.com/thentsation/bndes-data-pipeline/commit/da3cc1b529f0788fc0d63b988eed65ee5e945da8))

- **deps**: Update pyarrow requirement
  ([#22](https://github.com/thentsation/bndes-data-pipeline/pull/22),
  [`1ef07b3`](https://github.com/thentsation/bndes-data-pipeline/commit/1ef07b34b304c01e12b952dd15932236379b3e7e))

- **deps**: Update requests requirement
  ([#11](https://github.com/thentsation/bndes-data-pipeline/pull/11),
  [`8cc55c7`](https://github.com/thentsation/bndes-data-pipeline/commit/8cc55c7fb52babb7dbb515ab1681cf66e879c00a))

- **deps**: Update urllib3 requirement from <3.0,>=2.7 to >=2.8.0,<3.0
  ([#15](https://github.com/thentsation/bndes-data-pipeline/pull/15),
  [`a28d739`](https://github.com/thentsation/bndes-data-pipeline/commit/a28d7391d7e9f2ee0f72ae579843ecd6cdae38ce))


## v1.0.8 (2026-09-28)

### Bug Fixes

- Use RELEASE_PAT so dependabot auto-merge can write to PRs
  ([`b14146d`](https://github.com/thentsation/bndes-data-pipeline/commit/b14146dad253e777d133c0e5b4ecfea041c72ce2))


## v1.0.7 (2026-09-28)

### Bug Fixes

- Revert lambda/python 3.14 bump again and drop the no-op versions filter
  ([`f696f16`](https://github.com/thentsation/bndes-data-pipeline/commit/f696f160c0c92d8681bd9ea09415819cea603956))

### Chores

- **deps**: Bump lambda/python from 3.11 to 3.14
  ([#17](https://github.com/thentsation/bndes-data-pipeline/pull/17),
  [`2f89dfd`](https://github.com/thentsation/bndes-data-pipeline/commit/2f89dfd35dc3403896d831c6a279cf7d9ea6e1ab))


## v1.0.6 (2026-09-27)

### Bug Fixes

- Revert lambda/python 3.14 bump and match Dependabot's real dependency name
  ([`7a622db`](https://github.com/thentsation/bndes-data-pipeline/commit/7a622db5323aa354e35707b826d7ec0fcf7920c1))

### Chores

- **deps**: Bump lambda/python from 3.11 to 3.14
  ([#16](https://github.com/thentsation/bndes-data-pipeline/pull/16),
  [`55df222`](https://github.com/thentsation/bndes-data-pipeline/commit/55df222925240913fcd0cebe8ce0fc39fc86eb80))


## v1.0.5 (2026-09-26)

### Bug Fixes

- Revert lambda/python 3.14 bump a third time, block all versions
  ([`ca37854`](https://github.com/thentsation/bndes-data-pipeline/commit/ca37854c48c1032da5dd304eaec129790e221a2f))

### Chores

- **deps**: Bump lambda/python from 3.11 to 3.14
  ([#14](https://github.com/thentsation/bndes-data-pipeline/pull/14),
  [`8176c46`](https://github.com/thentsation/bndes-data-pipeline/commit/8176c4692f14f7478dc145a50fab99d0b6d9f57a))


## v1.0.4 (2026-09-26)

### Bug Fixes

- Ignore CVEs Trivy flags that aren't fixable or reachable here
  ([`54f8004`](https://github.com/thentsation/bndes-data-pipeline/commit/54f80043202cb2d7daf707e6a527b605876550db))

- Revert numpy>=2.5.3 auto-merge, ignore that range in dependabot
  ([`3939c68`](https://github.com/thentsation/bndes-data-pipeline/commit/3939c688b696310f6c6bce959a45cde3980e3e2c))

### Chores

- **deps**: Update numpy requirement from <2.3,>=1.26 to >=2.5.3,<2.6
  ([#13](https://github.com/thentsation/bndes-data-pipeline/pull/13),
  [`6538770`](https://github.com/thentsation/bndes-data-pipeline/commit/6538770b12e31f1a4a72d8cadc75276be95472da))


## v1.0.3 (2026-09-26)

### Bug Fixes

- Cap numpy below 2.3 - no wheels for this Lambda image at all
  ([`bbfe901`](https://github.com/thentsation/bndes-data-pipeline/commit/bbfe9013ffe93f30a138ea3a7f5cdb9f2172e43e))


## v1.0.2 (2026-09-26)

### Bug Fixes

- Pin the weekly lockfile refresh to Python 3.11 too
  ([`42105e5`](https://github.com/thentsation/bndes-data-pipeline/commit/42105e503c13ba64d43c436b5ead656d6e0a735b))

- Regenerate lockfile constrained to the Lambda's actual Python 3.11
  ([`1210efb`](https://github.com/thentsation/bndes-data-pipeline/commit/1210efb355bfa59b37f655df3be993ae6aab9b4c))


## v1.0.1 (2026-09-26)

### Bug Fixes

- Revert auto-merged Python 3.14 runtime bump that broke the build
  ([`4bf46bc`](https://github.com/thentsation/bndes-data-pipeline/commit/4bf46bcb741dc182a2ef657ab078f67af9310f82))

- Revert lambda/python 3.14 bump again (stale dependabot PR)
  ([`2ae8817`](https://github.com/thentsation/bndes-data-pipeline/commit/2ae88178ac435bba1a9f46ea6cad3e1a34b8171f))

### Chores

- **deps**: Bump boto3-stubs from 1.42.6 to 1.43.100
  ([#5](https://github.com/thentsation/bndes-data-pipeline/pull/5),
  [`4afea3d`](https://github.com/thentsation/bndes-data-pipeline/commit/4afea3d00d56bbe4746055607669f23c4e37867d))

- **deps**: Bump lambda/python from 3.11 to 3.14
  ([#12](https://github.com/thentsation/bndes-data-pipeline/pull/12),
  [`0072084`](https://github.com/thentsation/bndes-data-pipeline/commit/007208440483017724dbed4fc23a28a325fc580d))

- **deps**: Bump lambda/python from 3.11 to 3.14
  ([#9](https://github.com/thentsation/bndes-data-pipeline/pull/9),
  [`e224e12`](https://github.com/thentsation/bndes-data-pipeline/commit/e224e1279f6884737b0f90076b1070e4dc3dda47))

- **deps**: Bump ruff from 0.16.3 to 0.16.8
  ([#10](https://github.com/thentsation/bndes-data-pipeline/pull/10),
  [`ea56a49`](https://github.com/thentsation/bndes-data-pipeline/commit/ea56a49b683d692204d73acc67e232ef1757ff5e))

- **deps**: Bump types-requests from 2.32.4.20250913 to 2.33.0.20260906
  ([#7](https://github.com/thentsation/bndes-data-pipeline/pull/7),
  [`76dcebd`](https://github.com/thentsation/bndes-data-pipeline/commit/76dcebd54d685976da2f77693182c5732b9dc1b0))
