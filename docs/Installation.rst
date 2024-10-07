Installation
============

(Recommended) The Python Package Index 
--------------------------------------

The recommended way of installing MassDash is through the Python Package Index (PyPI). We recommend installing MassDash in its own virtual environment using Anaconda to avoid packaging conflicts.

First create a new environment:

.. code-block:: bash

   conda create --name=massdash python=3.9
   conda activate massdash 

Then in the new environment install MassDash.

.. code-block:: bash

   pip install massdash --upgrade

After installation the GUI can be launched in the Terminal/Anaconda Prompt using 

.. code-block:: bash

   massdash gui

Installation Guides
+++++++++++++++++++

.. toctree::
   :maxdepth: 1
   :hidden:

   installation_docs/windows_installation
   installation_docs/macos_installation
   installation_docs/ubuntu_installation

In depth installation guides can be found below:

1. :doc:`Windows Installation <installation_docs/windows_installation>` - Installation guide for Windows
2. :doc:`Mac Installation <installation_docs/macos_installation>` - Installation guide for Mac BigSur
3. :doc:`Ubuntu Installation <installation_docs/ubuntu_installation>` - Installation guide for Ubuntu


One Click Installation
----------------------

For those unfamilliar with commandline and only plan on using the GUI, a one click installation is also avaliable. Please see below for current releases.

.. |installwindows| image:: https://img.shields.io/badge/install-windows-blue?link=https%3A%2F%2Fgithub.com%2FRoestlab%2Fmassdash%2Freleases%2Fdownload%2Fv0.0.8%2Fmassdash_windows.exe
   :target: https://github.com/Roestlab/massdash/releases/download/v0.0.8/massdash_windows.exe
.. |installmacos| image::  https://img.shields.io/badge/install-macos-white?link=https%3A%2F%2Fgithub.com%2FRoestlab%2Fmassdash%2Freleases%2Fdownload%2Fv0.0.8%2Fmassdash_macos.pkg
   :target: https://github.com/Roestlab/massdash/releases/download/v0.0.8/massdash_macos.pkg
.. |installubuntu| image:: https://img.shields.io/badge/install-ubuntu-purple?link=https%3A%2F%2Fgithub.com%2FRoestlab%2Fmassdash%2Freleases%2Fdownload%2Fv0.0.8%2Fmassdash_linux.deb 
   :target: https://github.com/Roestlab/massdash/releases/download/v0.0.8/massdash_linux.deb
.. |demoapp| image:: https://img.shields.io/badge/demo-massdash.streamlit.app-brightgreen?link=https%3A%2F%2Fmassdash-test.streamlit.app%2F
   :target: https://massdash.streamlit.app/

|installwindows| |installmacos| |installubuntu|

For a one-click installation, click on the corresponding badge corresponding to your operating system, or visit the `latest release page <https://github.com/Roestlab/massdash/releases/latest>`_ and download the installer for your operating system.


Demo App
--------
|demoapp|

To test out MassDash please click `here <https://massdash.streamlit.app>`_.

.. note:: 

   The demo app is a simplified version of the MassDash GUI, and does not contain all the features of the full software.

Building from Source
--------------------

The source code is freely open and accessible on Github at https://github.com/Roestlab/massdash under the `BSD-3-Clause license <https://github.com/Roestlab/massdash?tab=BSD-3-Clause-1-ov-file>`_. The package can be installed by cloning and installing from source using pip.

First clone the repository:

.. code-block:: bash

        git clone git@github.com:Roestlab/massdash.git

Change into the massdash directory

.. code-block:: bash
        
        cd massdash

Install using pip

.. code-block:: bash

        pip install -e .

Docker Image
------------

MassDash is available as a docker image on dockerhub `here <https://github.com/Roestlab/massdash/pkgs/container/massdash>`_, ensure you have docker installed on your system, you can then pull the latest image of MassDash.

.. code-block:: bash

        docker pull ghcr.io/roestlab/massdash:latest 