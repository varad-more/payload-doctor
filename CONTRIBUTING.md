# Contributing

Keep changes focused: Payload Doctor is deliberately one frontend, one endpoint, and one Lambda. New dependencies or AWS services should solve a demonstrated need.

## Before opening a pull request

```bash
(cd backend && .venv/bin/pytest -q)
(cd frontend && npm ci && npm run build)
```

Add or update the smallest test that proves behavioral changes. Never commit payloads containing credentials, personal data, or customer information. Example payloads must be synthetic.
