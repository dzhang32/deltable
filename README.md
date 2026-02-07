# deltable

Get the delta between .rtf tables

## Installation

I recommend using [uv](https://docs.astral.sh/uv/) to manage the python version, virtual environment and `deltable` installation:

```bash
uv venv --python 3.10
source .venv/bin/activate
uv pip install deltable
```

## Additional setup

### Code coverage

- Add a "CODECOV_TOKEN" secret (obtained from [here](https://app.codecov.io/gh/dzhang32/test_python_package/)) to your repo via `Settings` -> `Secrets and variables` -> `Actions`.
