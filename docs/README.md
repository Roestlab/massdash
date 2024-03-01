# MassDash Documentation

*** 

Documentation for the MassDash project is built using [sphinx](https://www.sphinx-doc.org/en/master/) and is hosted on Read the Docs [MassDash](https://massdash.readthedocs.io/en/latest/).

## Building the Documentation

To build the documentation locally, you will need to install the following dependencies in requirements.txt:

```bash
pip -r requirements.txt
```

Then you can build the documentation using the following command (assuming you are in the docs directory):

```bash
sphinx-build -b html ./source ./build
```