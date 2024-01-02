Loading Data
############


To load data into MassSeer, a loader object must be initiated. There are two types of loader classes
1. Chromatogram Loaders: Raw data stores chromatograms, this allows for faster loading however since extraction has already been performed by the upstream analysis tool.
2. Spectrum Loaders: These data types are slower to load however it leads to more customization since raw data can be extracted on the fly and parameters such as ion mobility, m/z or retention time extraction window can be adjusted.

Currently avaliable loaders are:

Chromatogram Loaders
--------------------
:py:class:`~massseer.loaders.SqMassLoader`

Spectrum Loaders
----------------
:py:class:`~massseer.loaders.MzMLDataLoader`

Since each loader type is linked with a results file each loader can be used to extract information on the features the DIA algorithms found. For more information on extracting features, :doc:`here<Loading Feature Information>` 

Click below for more information on each loader type:
-----------------------------------------------------
.. toctree::
   :maxdepth: 2

   Loading Feature Information
   Loading Raw Data

Have an idea for a loader you want to see? Create a issue `here <https://github.com/Roestlab/massseer/issues>`_.
