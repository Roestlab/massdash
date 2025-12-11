"""
massdash/testing/NumpySnapshotExtension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

# Taken from https://github.com/atharva-2001/syrupy-pandas-numpy/blob/main/tests/test_np.py
from typing import Any
import numpy as np
from syrupy.data import SnapshotCollection
from syrupy.extensions.single_file import SingleFileSnapshotExtension
from syrupy.types import SerializableData

class NumpySnapshotExtension(SingleFileSnapshotExtension):
    """
    Handles Numpy Snapshots. Snapshots are stored as dat files and the numpy arrays are compared using numpy testing methods.
    """
    _file_extension = "dat"

    def matches(self, *, serialized_data, snapshot_data):
        try:
            # Both are now bytes, need to deserialize for comparison
            import io
            snapshot_array = np.loadtxt(io.BytesIO(snapshot_data))
            serialized_array = np.loadtxt(io.BytesIO(serialized_data))
            if np.testing.assert_allclose(snapshot_array, serialized_array, atol=1e-08, rtol=1e-05) is not None:
                return False
            else: return True
        except:
            return False

    def _read_snapshot_data_from_location(
        self, *, snapshot_location: str, snapshot_name: str, session_id: str
    ):
        # see https://github.com/tophat/syrupy/blob/f4bc8453466af2cfa75cdda1d50d67bc8c4396c3/src/syrupy/extensions/base.py#L139
        try:
            with open(snapshot_location, 'rb') as f:
                return f.read()
        except OSError:
            return None

    @classmethod
    def _write_snapshot_collection(
        cls, *, snapshot_collection: SnapshotCollection
    ) -> None:
        # see https://github.com/tophat/syrupy/blob/f4bc8453466af2cfa75cdda1d50d67bc8c4396c3/src/syrupy/extensions/base.py#L161
        
        filepath, data = (
            snapshot_collection.location,
            next(iter(snapshot_collection)).data,
        )
        # Write bytes directly to file
        with open(filepath, 'wb') as f:
            f.write(data)

    def serialize(self, data: SerializableData, **kwargs: Any) -> bytes:
        import io
        buffer = io.BytesIO()
        np.savetxt(buffer, data, fmt='%.18e')
        return buffer.getvalue()
    
    def diff_lines(self, serialized_data, snapshot_data):
        try:
            import io
            snapshot_array = np.loadtxt(io.BytesIO(snapshot_data))
            serialized_array = np.loadtxt(io.BytesIO(serialized_data))
            np.testing.assert_allclose(snapshot_array, serialized_array, atol=1e-08, rtol=1e-05)
        except AssertionError as e:
            return str(e).split('\n')