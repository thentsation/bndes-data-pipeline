# CHANGELOG

<!-- version list -->

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
