"""
massdash/testing
~~~~~~~~~~~~~~~~

The :mod:`massdash.testing` subpackage contains classes for testing massdash. SnapShotExtension classes are based off of syrupy snapshots
"""

from .NumpySnapshotExtension import NumpySnapshotExtenstion
from .PandasSnapshotExtension import PandasSnapshotExtenstion

__all__ = [ 
            "NumpySnapshotExtenstion",
            "PandasSnapshotExtenstion"]