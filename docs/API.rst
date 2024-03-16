API
===

Note: This section provides a comprehensive overview of all methods and classes avaliable in MassDash. This content is generated automatically using sphinx autosummary and autodoc based on the python documentation.

:mod:`massdash.structs`: Internal Structures For storing data
*************************************************************

.. automodule:: massdash.structs
   :no-members:
   :no-inherited-members:

Abstract Classes
----------------

.. currentmodule:: massdash

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst

   structs.Data1D
   structs.GenericFeature
   structs.GenericStructCollection
 
Classes 
-------
.. currentmodule:: massdash

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst
   
   structs.Chromatogram
   structs.Mobilogram
   structs.Spectrum
   structs.TransitionGroup
   structs.TransitionGroupFeature
   structs.TransitionFeature
   structs.FeatureMap
   structs.TargetedDIAConfig

Collections
-----------
-----------
.. currentmodule:: massdash

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst
   
   structs.TransitionGroupCollection
   structs.TransitionGroupFeatureCollection
   structs.FeatureMapCollection
   structs.TopTransitionGroupFeatureCollection




:mod:`massdash.loaders`: Classes for loading data 
*************************************************

.. automodule:: massdash.loaders
   :no-members:
   :no-inherited-members:

.. currentmodule:: massdash.loaders

Abstract Classes
----------------

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst

   GenericLoader
   GenericChromatogramLoader
   GenericSpectrumLoader

Classes
-------

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst
   
   MzMLDataLoader
   SqMassLoader
   SpectralLibraryLoader

:mod:`massdash.plotting`: Classes for plotting data 
***************************************************

.. automodule:: massdash.plotting
   :no-members:
   :no-inherited-members:

.. currentmodule:: massdash.plotting

Abstract Classes
----------------

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst

   GenericPlotter

Classes
-------

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst
   
   PlotConfig
   InteractivePlotter
   InteractiveTwoDimensionPlotter
   InteractiveThreeDimensionPlotter

:mod:`massdash.peakPickers`: Classes for Peak Picking 
*****************************************************

.. automodule:: massdash.peakPickers
   :no-members:
   :no-inherited-members:

.. currentmodule:: massdash.peakPickers

Abstract Classes
----------------

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst

   GenericPeakPicker

Classes
-------

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst
   
   MRMTransitionGroupPicker
   pyMRMTransitionGroupPicker
   ConformerPeakPicker

:mod:`massdash.testing`: Classes for testing 
********************************************
.. automodule:: massdash.testing
   :no-members:
   :no-inherited-members:

.. currentmodule:: massdash.testing

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst

   NumpySnapshotExtension
   PandasSnapshotExtension
   BokehSnapshotExtension
   PlotlySnapshotExtension
