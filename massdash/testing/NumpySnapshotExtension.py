# Taken from https://github.com/atharva-2001/syrupy-pandas-numpy/blob/main/tests/test_np.py
from typing import Any
import numpy as np
from syrupy.data import SnapshotCollection
from syrupy.extensions.single_file import SingleFileSnapshotExtension
from syrupy.types import SerializableData

class NumpySnapshotExtenstion(SingleFileSnapshotExtension):
    _file_extension = "dat"

    def matches(self, *, serialized_data, snapshot_data):
        try:
            if np.allclose(np.array(snapshot_data), np.array(serialized_data)):
                return True
            else: return True
        except:
            return False

    def _read_snapshot_data_from_location(
        self, *, snapshot_location: str, snapshot_name: str, session_id: str
    ):
        # see https://github.com/tophat/syrupy/blob/f4bc8453466af2cfa75cdda1d50d67bc8c4396c3/src/syrupy/extensions/base.py#L139
        try:
            return np.loadtxt(snapshot_location).tolist()
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
        np.savetxt(filepath, data)

    def serialize(self, data: SerializableData, **kwargs: Any) -> str:
        return data