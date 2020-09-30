# DPMFA

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4059650.svg)](https://doi.org/10.5281/zenodo.4059650)

If you run into any problems please create a new issue at the [upstream repository](https://github.com/isr-ifi/dpmfa/issues).

## Usage example

0. [Optional] Create a virtual environment for the project:
```bash
$ mkvirtualenv dpmfa
```

1. Install the package:

```bash
$ pip install dpmfa
```

2. Download the example from this repository, then install the required dependencies:

```bash
$ pip install -r example/requirements.txt
```

3. Then, run the example:

```bash
$ python example/plots.py
```

You should now have a directory `experiment_output/` with the results of the
example simulation.

## Development

First, clone the repo:

```bash
$ git clone <url-of-this-repo>
```

[Optional] Create a virtual environment for the project:
```bash
$ mkvirtualenv dpmfa
```

Install the required dependencies:
```bash
$ pip install -r requirements.txt -r requirements-dev.txt
```

Install the git hooks with pre-commit:
```bash
$ pre-commit install
```

Running tests:
```bash
$ py.test
````
