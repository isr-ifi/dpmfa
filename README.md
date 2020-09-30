# DPMFA

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4059650.svg)](https://doi.org/10.5281/zenodo.4059650)

If you run into any problems please use create a new issue at the [upstream repository](https://github.com/isr-ifi/dpmfa/issues).

## Usage example

First, clone the repository:

```bash
$ git clone <url-of-this-repo>
```

[Optional] Create a virtual environment for the project:
```bash
$ mkvirtualenv dpmfa
```

Install the required dependencies:
```bash
$ pip install -r requirements.txt
```

Then, run the example:

```bash
$ python example/plots.py
```

You should now have a directory `example_output/` with the results of the
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
