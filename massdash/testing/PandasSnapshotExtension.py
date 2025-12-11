"""
massdash/testing/PandasSnapshotExtension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
# Taken from https://github.com/atharva-2001/syrupy-pandas-numpy/blob/main/tests/test_pd.py
from typing import Any
import pickle
from syrupy.data import SnapshotCollection
from syrupy.extensions.single_file import SingleFileSnapshotExtension
import pandas as pd
from syrupy.types import SerializableData

class PandasSnapshotExtension(SingleFileSnapshotExtension):
    """
    Handles Pandas Snapshots. Snapshots are stored as raw files (pickled) and the dataframes are compared using pandas testing methods
    """
    _file_extension = "raw"

    def matches(self, *, serialized_data, snapshot_data):
        try:
            # Both are now bytes, need to deserialize for comparison
            serialized_df = pickle.loads(serialized_data)
            snapshot_df = pickle.loads(snapshot_data)
            
            if pd.testing.assert_frame_equal(serialized_df, snapshot_df) is not None:
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
        return pickle.dumps(data)
    
    def diff_lines(self, serialized_data, snapshot_data):
        try:
            serialized_df = pickle.loads(serialized_data)
            snapshot_df = pickle.loads(snapshot_data)
            pd.testing.assert_frame_equal(serialized_df, snapshot_df)
        except AssertionError as e:
            return (["Snapshot:"] +
                    snapshot_df.to_string().split('\n') + 
                    ['-------------------------------'] +
                    ["Serialized:"] +
                    serialized_df.to_string().split('\n') +
                    str(e).split('\n'))