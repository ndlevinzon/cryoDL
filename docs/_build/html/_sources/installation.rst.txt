Installation
============

cryoDL is a Python package that provides an interactive CLI for managing cryo-EM software wrappers. This guide will help you install cryoDL and its dependencies.

Prerequisites
------------

* Python 3.8 or higher
* pip (Python package installer)
* Git (for cloning the repository)

Installation Methods
-------------------

From Source (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/ndlevinzon/cryoDL.git
      cd cryoDL

2. Install in development mode:

   .. code-block:: bash

      pip install -e .

   Or use the provided installation script:

   .. code-block:: bash

      # On Linux/macOS
      ./install.sh

      # On Windows
      install.bat

3. Verify the installation:

   .. code-block:: bash

      cryodl --help

From PyPI (Future Release)
~~~~~~~~~~~~~~~~~~~~~~~~~

When cryoDL is published to PyPI, you'll be able to install it with:

.. code-block:: bash

   pip install cryodl

Dependencies
------------

Core Dependencies
~~~~~~~~~~~~~~~~

cryoDL has minimal core dependencies, using only Python standard library modules for basic functionality:

* No external dependencies required for basic configuration management
* All core functionality uses built-in Python modules

Analysis Dependencies
~~~~~~~~~~~~~~~~~~~~

For advanced analysis features (Topaz cross-validation analysis), install additional packages:

.. code-block:: bash

   pip install numpy pandas matplotlib pillow seaborn

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~

For enhanced functionality, you may want to install:

.. code-block:: bash

   pip install scipy  # For additional scientific computing features

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

For development and testing:

.. code-block:: bash

   pip install pytest black flake8 mypy

Documentation Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~

For building documentation:

.. code-block:: bash

   pip install sphinx sphinx-rtd-theme sphinx-copybutton myst-parser

External Software Dependencies
-----------------------------

cryoDL is designed to wrap external cryo-EM software. You'll need to install and configure:

Topaz
~~~~~

Install Topaz for particle picking and analysis:

.. code-block:: bash

   # Using conda (recommended)
   conda install -c conda-forge topaz

   # Or from source
   git clone https://github.com/tbepler/topaz.git
   cd topaz
   pip install -e .

ModelAngelo
~~~~~~~~~~~

Install ModelAngelo for protein structure prediction:

.. code-block:: bash

   # Using conda
   conda install -c conda-forge model-angelo

   # Or from source
   git clone https://github.com/3dem/model-angelo.git
   cd model-angelo
   pip install -e .

SLURM (Optional)
~~~~~~~~~~~~~~~

For cluster computing support, ensure SLURM is installed on your system:

.. code-block:: bash

   # On Ubuntu/Debian
   sudo apt-get install slurm-wlm

   # On CentOS/RHEL
   sudo yum install slurm

Configuration
-------------

After installation, initialize cryoDL:

.. code-block:: bash

   cryodl
   cryoDL> init
   cryoDL> add_dependency topaz /path/to/topaz
   cryoDL> add_dependency model_angelo /path/to/model-angelo

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

1. **Import Error**: If you get import errors, ensure you're in the correct Python environment:

   .. code-block:: bash

      python -c "import sys; print(sys.path)"

2. **Command Not Found**: If `cryodl` command is not found:

   .. code-block:: bash

      # Check if the package is installed
      pip list | grep cryodl

      # Reinstall if needed
      pip install -e .

3. **Permission Errors**: On Linux/macOS, you might need:

   .. code-block:: bash

      chmod +x install.sh

4. **Missing Dependencies**: Install missing packages:

   .. code-block:: bash

      pip install -r requirements.txt

Getting Help
-----------

If you encounter issues:

1. Check the :ref:`troubleshooting` section
2. Review the :ref:`examples` for usage patterns
3. Open an issue on the GitHub repository
4. Check the logs in the current directory (cryodl.log)

Next Steps
----------

After installation, proceed to:

* :ref:`quickstart` - Get started with cryoDL
* :ref:`cli_commands` - Learn about available commands
* :ref:`configuration` - Configure dependencies and settings
