# Changelog

All notable changes to `ablechart` will be documented in this file.

## 0.1.1 - 2026-06-21

Security hardening (no exploitable issue in 0.1.0; defense-in-depth):

- Relax `lxml` pin to `>=5,<7` so installs can resolve to the patched 6.1.0+
  (PYSEC-2026-87 ships a safe `resolve_entities` default). ablechart never calls
  lxml parsers directly; XML reads go through python-pptx, which already rejects
  DOCTYPE / external entities. Verified against lxml 6.1.0.
- Pin all GitHub Actions to full commit SHAs (with version comments) in the CI
  and publish workflows, removing mutable-tag supply-chain risk on the
  OIDC-publishing pipeline.

## 0.1.0 - 2026-06-21

Initial public package candidate.

Supported scope:

- editable native PowerPoint combo charts
- waterfall, scatter, bubble, and range snapshot chart families
- semantic metadata round-trip for generated charts
- chart inventory and template-safe data replacement for the first-batch native chart types
- experimental semantic component families for single-slide financial report panels

Packaging:

- MIT license
- Python `>=3.10`
- PyPI metadata and source distribution manifest prepared
- Release-readiness tests for license, package metadata, README positioning, and sdist manifest
- GitHub Actions CI plus TestPyPI / PyPI Trusted Publishing workflow prepared
