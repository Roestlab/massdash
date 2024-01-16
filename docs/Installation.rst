Installation
============

The Python Package Index
------------------------

MassDash is available as a python package on the python package index, and can be installed by pip in a terminal or cmd prompt.

.. code-block:: bash

        pip install massdash

Building from Source
--------------------

The source code is freely open and accessible on Github at https://github.com/Roestlab/massdash under the `BSD-3-Cluase license <https://github.com/Roestlab/massdash?tab=BSD-3-Clause-1-ov-file>`. The package can be installed by cloning and installing from source using pip.

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

        docker pull singjust/massdash:latest

