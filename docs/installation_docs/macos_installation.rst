MassDash Installation on MacOS Big Sur
======================================

This guide will help you install MassDash on MacOS Big Sur.

.. note::
    This tutorial was created using a clean installation of MacOS Big Sur using a virtual machine. The virtual machine was created using Oracle VM VirtualBox, with 32Gb of RAM, 8 processors, and 64Gb of storage. The virtual machine was created using the macOS Big Sur iso file from `The Internet Archive <https://archive.org/details/mac-osx-big-sur-iso>`_.

Prerequisites
-------------

It is recommended to use Anaconda to manage Python environments and packages. You can download Anaconda from `here <https://www.anaconda.com/download>`_. You can find documentation for installing Anaconda on MacOS `here <https://docs.anaconda.com/free/anaconda/install/mac-os/>`__.

Installation
------------

1. Launch a terminal and create a new conda environment using the following command:

   .. code-block:: bash

      conda create -n massdash python=3.9 -y

.. image:: ./assets/img/macos_conda_create_env.png
   :alt: Create a new conda environment
   :align: center

2. Activate the new conda environment using the following command:

    .. code-block:: bash
    
        conda activate massdash

.. image:: ./assets/img/macos_conda_env_activate.png
    :alt: Activate the new conda environment
    :align: center

3. Install massdash using the following command:

    .. code-block:: bash

        pip install massdash

.. image:: ./assets/img/macos_massdash_install.png
    :alt: Install massdash
    :align: center

Usage
-----

Help
~~~~

You can get help on how to use MassDash's GUI by running the following command in the terminal:

.. code-block:: bash

    massdash gui --help

.. image:: ./assets/img/macos_conda_cmd_massdash_gui_help.png

Launch MassDash GUI
~~~~~~~~~~~~~~~~~~~

You can launch MassDash's GUI by running the following command in the terminal:

.. code-block:: bash

    massdash gui

A browser window will open with the MassDash GUI. If the browser window does not open, you can navigate to the following URL in your browser using the local url provided in the Anaconda CMD.exe output, by default it should be `http://localhost:8501/`, unless the port is changed.

.. note::
    It is recommended to use Google Chrome or Firefox to open the MassDash GUI instead of Safari.

.. note::
    MassDash warns you that onnxruntime, torch, and torchmeets are not installed. You can ignore this warning if you do not plan to use the MassDash's peak picking conformer model. 

.. image:: ./assets/img/macos_conda_cmd_massdash_gui_run.png

Once the browser window opens, you can start using MassDash's GUI to visualize your mass spectrometry data. For more information on the GUI, please refer to the `MassDash GUI Documentation <../GUI.rst>`_.

.. image:: ./assets/img/macos_massdash_gui.png
.. image:: ./assets/img/macos_massdash_gui_example.png
