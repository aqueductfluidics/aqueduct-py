<p><img src="https://github.com/aqueductfluidics/.github/blob/main/profile/assets/images/logo_blue.svg" alt="Aqueduct Fluidics" /></p>

# Aqueduct Fluidics Python API

The Aqueduct Fluidics Python API is a Python-based software package designed for laboratory automation and instrumentation. It provides an abstraction layer that allows operators to write Python code to interface with devices such as pumps, valves, and sensors, without having to deal with low-level communication protocols.

You can find complete documentation here [here](https://docs.aqueductfluidics.com).

## Getting Started

To get started with the Aqueduct Fluidics Core Application, simply install it using `pip`:

```bash
pip install aqueduct-py
```

## Testing

Install with dev dependencies.

Windows

```text
python -m pip install -e .[test]
```

Mac

```text
python -m pip install -e '.[test]'
```

To test

```text
python -m pytest src
```

## Pre-Commit Hooks

```text
pre-commit run --all-files
```
