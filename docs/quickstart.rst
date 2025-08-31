Quickstart Guide
===============

This guide will help you get started with cryoDL in just a few minutes.

Prerequisites
------------

* cryoDL installed (see :ref:`installation`)
* Python 3.8 or higher
* Basic familiarity with command line interfaces

Getting Started
--------------

1. **Launch cryoDL**

   Open your terminal and run:

   .. code-block:: bash

      cryodl

   You should see the cryoDL banner and interactive prompt:

   .. code-block:: text

      ===========================================
      === cryoDL Interactive Configuration Manager ===
      ===========================================

      Type 'help' for available commands, 'quit' to exit.
      All interactions are logged to cryodl.log in the current directory.

      cryoDL>

2. **Initialize Configuration**

   Start by initializing the default configuration:

   .. code-block:: bash

      cryoDL> init

   This creates a `config.json` file with default settings.

3. **Add Dependencies**

   Configure paths to your cryo-EM software:

   .. code-block:: bash

      cryoDL> add_dependency topaz /usr/local/bin/topaz
      cryoDL> add_dependency model_angelo /usr/local/bin/model-angelo

4. **Validate Dependencies**

   Check that all dependencies are properly configured:

   .. code-block:: bash

      cryoDL> validate_dependencies

Basic Commands
-------------

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # View current configuration
   cryoDL> show

   # Get specific configuration value
   cryoDL> get dependencies.topaz.path

   # Set configuration value
   cryoDL> set settings.max_threads 8

   # List all dependencies
   cryoDL> list_dependencies

File Operations
~~~~~~~~~~~~~~

.. code-block:: bash

   # Show current directory
   cryoDL> pwd

   # List files
   cryoDL> ls

   # Clear screen
   cryoDL> clear

Working with Topaz
-----------------

Preprocessing
~~~~~~~~~~~~

Run Topaz preprocessing locally:

.. code-block:: bash

   cryoDL> topaz preprocess --local

   # Follow the prompts to enter:
   # - Raw micrographs directory
   # - Particle coordinates file (optional)
   # - Output directory
   # - Pixel size for downsampling

Submit to SLURM cluster:

.. code-block:: bash

   cryoDL> topaz preprocess

   # Same prompts, but generates SLURM job

Cross-Validation
~~~~~~~~~~~~~~~

Run cross-validation with automatic analysis:

.. code-block:: bash

   cryoDL> topaz cross --local

   # This will:
   # 1. Preprocess micrographs
   # 2. Convert particle coordinates
   # 3. Perform train-test split
   # 4. Run cross-validation training
   # 5. Automatically analyze results

Denoising
~~~~~~~~~

Run Topaz denoising workflow:

.. code-block:: bash

   cryoDL> topaz denoise --local

   # This will:
   # 1. Split movie frames into even/odd training data
   # 2. Train a denoising model
   # 3. Apply the model to denoise micrographs
   # 4. Generate visualization plots

Submit to SLURM:

.. code-block:: bash

   cryoDL> topaz denoise

   # Same workflow but submitted to SLURM cluster

Working with ModelAngelo
-----------------------

Run ModelAngelo locally:

.. code-block:: bash

   cryoDL> model_angelo --local

   # Follow prompts for:
   # - MRC file path
   # - FASTA file path

Submit to SLURM:

.. code-block:: bash

   cryoDL> model_angelo

Analysis
--------

Analyze existing cross-validation results:

.. code-block:: bash

   cryoDL> analyze_cv saved_models/EMPIAR-10025/cv

   # This generates:
   # - Performance plots
   # - Analysis summaries
   # - Recommendations

SLURM Integration
----------------

View SLURM configuration:

.. code-block:: bash

   cryoDL> slurm_show

Update SLURM settings:

.. code-block:: bash

   cryoDL> slurm_update --nodes 2 --gres-gpu 2 --time 12:00:00

Generate SLURM header:

.. code-block:: bash

   cryoDL> slurm_generate --job-name my_job --nodes 1 --gres-gpu 1

Getting Help
-----------

.. code-block:: bash

   # Show all available commands
   cryoDL> help

   # Get help for specific command
   cryoDL> help topaz

   # Show command usage
   cryoDL> help model_angelo

Exiting
-------

.. code-block:: bash

   cryoDL> quit

   # Or use Ctrl+D

Example Workflow
---------------

Here's a complete example workflow:

.. code-block:: bash

   # 1. Start cryoDL
   cryodl

   # 2. Initialize and configure
   cryoDL> init
   cryoDL> add_dependency topaz /usr/local/bin/topaz
   cryoDL> validate_dependencies

   # 3. Run Topaz preprocessing
   cryoDL> topaz preprocess --local
   # Enter: /path/to/micrographs
   # Enter: /path/to/particles.txt
   # Enter: output_dir
   # Enter: 8

   # 4. Run cross-validation
   cryoDL> topaz cross --local
   # Enter: /path/to/micrographs
   # Enter: /path/to/particles.txt
   # Enter: cv_output
   # Enter: 8
   # Enter: 10
   # Enter: 5
   # Enter: 250,300,350,400,450,500

   # 5. View results
   cryoDL> ls cv_output/saved_models/cv/

   # 6. Exit
   cryoDL> quit

Next Steps
----------

* :ref:`cli_commands` - Detailed command reference
* :ref:`configuration` - Advanced configuration options
* :ref:`examples` - More complex usage examples
* :ref:`troubleshooting` - Common issues and solutions
