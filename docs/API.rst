API
===

Note: This section provides a comprehensive overview of all methods and classes avaliable in MassSeer. This content is generated automatically using sphinx autosummary and autodoc based on the python documentation.

:mod:`masseer.structs`: Internal Structures For storing data
============================================================

.. automodule:: massseer.structs
   :no-members:
   :no-inherited-members:

Abstract Classes
----------------

.. currentmodule:: massseer

.. autosummary::
   :nosignatures:
   :toctree: generated/
   :template: class.rst

   structs.Data1D
 
Classes 
-------
.. currentmodule:: massseer

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


:mod:`masseer.loaders`: Classes for loading data 
================================================

.. automodule:: massseer.loaders
   :no-members:
   :no-inherited-members:

.. currentmodule:: massseer.loaders

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

:mod:`masseer.plotting`: Classes for plotting data 
==================================================

.. automodule:: massseer.plotting
   :no-members:
   :no-inherited-members:

.. currentmodule:: massseer.plotting

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

:mod:`masseer.peakPickers`: Classes for Peak Picking 
====================================================

.. automodule:: massseer.peakPickers
   :no-members:
   :no-inherited-members:

.. currentmodule:: massseer.peakPickers

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

