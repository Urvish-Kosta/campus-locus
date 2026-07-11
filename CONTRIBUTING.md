# Contributing

Thanks for your interest in improving Campus Locus. Contributions of all sizes
are welcome — bug reports, documentation fixes, and features.

## Getting set up

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
cd backend && python -m app.seed && flask --app wsgi run
```

## Before you open a pull request

1. **Run the tests** — `pytest tests/ -q` must pass.
2. **Keep changes focused** — one logical change per pull request.
3. **Match the existing style** — small, readable functions; comments only where
   they explain *why*, not *what*.
4. **Update docs** — if you change the API or behaviour, update the relevant file
   in `docs/` and the README.

## Commit messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat:     a new feature
fix:      a bug fix
docs:     documentation only
refactor: a code change that neither fixes a bug nor adds a feature
perf:     a performance improvement
test:     adding or correcting tests
build:    build system or dependency changes
ci:       CI configuration changes
chore:    maintenance
```

Example: `feat(api): add step-free option to route endpoint`

## Reporting bugs

Open an issue describing what you did, what you expected, and what happened.
Include your OS, browser, and Python version where relevant.
