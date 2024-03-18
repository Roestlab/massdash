"""
test/structs/test_GenericStructCollection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from massdash.structs.GenericStructCollection import GenericStructCollection

def test_get_runs():
    collection = GenericStructCollection()
    collection["run1"] = "data1"
    collection["run2"] = "data2"
    collection["run3"] = "data3"

    runs = collection.getRuns()

    assert len(runs) == 3
    assert "run1" in runs
    assert "run2" in runs
    assert "run3" in runs
