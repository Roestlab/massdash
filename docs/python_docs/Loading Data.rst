Loading Data
================

.. currentmodule:: massdash.loaders

To load raw data into MassDash, a loader object must be initiated. There are two types of loader classes


1. :py:class:`Chromatogram Loaders<GenericChromatogramLoader>`: Chromatogram Loaders: Raw data stores chromatograms, this allows for faster loading however since extraction has already been performed by the upstream analysis tool. This includes :py:class:`SqMassLoader`
2. :py:class:`Spectrum Loaders<GenericSpectrumLoader>`: These data types are slower to load however it leads to more customization since raw data can be extracted on the fly and parameters such as ion mobility, m/z or retention time extraction window can be adjusted. This includes :py:class:`MzMLDataLoader`


**Click below for more information on each loader type:**

- :doc:`Loading Chromatogram Data`
- :doc:`Loading Spectrum Data`

Since each loader type is linked with a results file each loader can be used to extract information on the features the DIA algorithms found. For more information on extracting features, :doc:`here<Loading Feature Information>` 

.. toctree::
   :maxdepth: 2
   :hidden:

   Loading Chromatogram Data
   Loading Spectrum Data
   Loading Feature Information

Have an idea for a loader you want to see? Create a issue `here <https://github.com/Roestlab/massdash/issues>`_.

