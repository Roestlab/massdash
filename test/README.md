# Testing 

Tests are performed using [Pytest](https://docs.pytest.org/en/8.0.x/) and [Syrupy](https://github.com/tophat/syrupy). <br> [Syrupy](https://github.com/tophat/syrupy) is used to compare output to previous expected output states. 

Install required dependecies using

`pip install -r requirements-dev.txt`

For conformer tests, optional dependencies are also required and can be installed with.

`pip install -r requirements-optional.txt`

## Running Tests

Execute the following command in massdash/ base folder:

```bash
python -m pytest --snapshot-warn-unused test/
```

For verbose output:
```bash
python -m pytest --snapshot-warn-unused test/
```

To update snapshots:
```bash
python -m pytest --snapshot-update test/
```
> **_NOTE:_**  CI github testing sometimes fails on mac failing to find pytest. If this occurs please rerun. 