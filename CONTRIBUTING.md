# Contributing

Contributions should help developers understand, test and implement safer AI action paths in their **own authorized development environments**.

1. Propose a narrowly-scoped change in a GitHub issue or pull request.
2. Add a synthetic offline example and tests, without credentials or live data.
3. Keep factor modes honest: `ENFORCEMENT` (local reference preflight), `ADVISORY`, or `RECORD_ONLY`.
4. Never represent untested capabilities as a certified security, fairness or legal result.
5. Run `PYTHONPATH=src python -m unittest discover -s tests -t . -v` before submitting.

Copyright remains with contributors subject to the Apache License 2.0. By submitting a contribution, you agree it can be redistributed under Apache 2.0. Respect TRUSTELIS brand ownership.
