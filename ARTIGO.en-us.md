[🇧🇷 Português](ARTIGO.md) | 🇺🇸 English

# A network failure disguised as "no data"

This is, by far, the most mature repository I productized in this batch — it already had four CI pipelines (lint, tests, security scan, an actual Lambda container build-and-run test), Trivy, well-built mocked tests, a Dockerfile with an existing urllib3 CVE workaround. This wasn't an abandoned project. And it still had one specific kind of bug: silent, and only visible when the network fails — exactly when you most need to know something went wrong.

## The bug: a network error disguised as "no data found"

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
        # the function just ends here, nothing re-raised
```

If the BNDES API were down, returned a 500, or DNS failed, this function would simply log the error and **stop yielding items** — without re-raising the exception. From the caller's (`lambda_handler`'s) point of view, this is indistinguishable from "there's no balance sheet for this year":

```python
for name, df in fetch_resources_by_year(year):
    ...
if not all_dfs:
    return {"statusCode": 404, "body": ...}  # "No data found for year {year}"
```

A real infrastructure failure turns into an ordinary `404`, not a `500`. And the whole pipeline explicitly documents that CloudWatch alarms and SNS notifications exist to catch errors — but a `404` isn't an error to CloudWatch, it's a valid response from the function. A day of BNDES API downtime would slip through with no alarm, nothing in SNS, and nobody would know a day of data was missing until noticing the gap in S3 weeks later.

## The fix: let the error propagate

```python
def fetch_resources_by_year(year, dataset_id="balanco-patrimonial"):
    ...
    response = requests.get(pkg_url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    ...
    yield name, df
```

I removed the catch-all `try/except`. A network failure now propagates up to `lambda_handler`'s own `try/except`, which already existed and already did the right thing — return `statusCode: 500` with the error message. No new logic, just no longer hiding the symptom one level below where it was already handled correctly.

While there, I added `timeout=30` to both `requests.get` calls (there was no timeout anywhere before - in a Lambda with a 900s limit, a hung connection would burn the entire execution budget without ever raising an error).

## A detail that only surfaced on a calm read: `process_data` called and its result ignored

```python
for name, df in fetch_resources_by_year(year):
    if not df.empty:
        process_data(df)          # return value discarded
        all_dfs.append(df)        # uses the "original" df
```

This isn't a bug — `process_data` does `df.dropna(inplace=True)`, so the mutation happens on the same object that gets appended afterward. It works by implementation accident, not by design. I made it explicit (`df = process_data(df)`), because the next person who touches `process_data` and swaps `inplace=True` for a copy would silently introduce the exact same kind of bug I just fixed in `fetch_data.py`.

## The rest: types, tests, modernized CI

Added type hints throughout (mypy clean), swapped `black`+`flake8` for `ruff` (the rest of the org's standard), pinned `requests`/`urllib3`/`pyarrow` (they had known CVEs, fixed by the bump), and wrote tests for the paths that were missing: `save_data` writing locally and to S3, the `ValueError` when neither a bucket nor a local dir is configured, the network error actually propagating, and the branch where a resource matches the year but its datastore has no records. Coverage went from ~74% to 100% of the modules under `src/`.

The four existing pipelines (lint, tests, security scan, build+run) keep doing what they already did well — I just modernized the action versions, swapped the linter, and layered the rest of the org's pattern on top: dependabot (pip, docker, terraform, github-actions), semantic release, and a scheduled dependency scan. I didn't touch the Terraform beyond letting dependabot watch provider versions - the infrastructure pipeline already doesn't run `apply`/`destroy` automatically, and this wasn't the moment for me to decide to change that.
