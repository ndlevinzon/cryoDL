API Reference
=============

This section provides detailed API documentation for the cryoDL package, automatically generated from the source code.

Core Modules
------------

.. automodule:: src.config_manager
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: src.cli
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: src.topaz_analysis
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: src.build_fasta
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Configuration Manager
--------------------

The :class:`ConfigManager` class is the core component for managing cryoDL configuration.

.. autoclass:: src.config_manager.ConfigManager
   :members:
   :special-members: __init__

   .. automethod:: __init__

   .. automethod:: create_default_config

   .. automethod:: load_config

   .. automethod:: save_config

   .. automethod:: get

   .. automethod:: set

   .. automethod:: update_dependency_path

   .. automethod:: validate_dependency_path

   .. automethod:: list_dependencies

   .. automethod:: generate_slurm_header

   .. automethod:: get_slurm_config

   .. automethod:: update_slurm_config

Interactive CLI Shell
--------------------

The :class:`CryoDLShell` class provides the interactive command-line interface.

.. autoclass:: src.cli.CryoDLShell
   :members:
   :special-members: __init__

   .. automethod:: __init__

   .. automethod:: setup_logging

   .. automethod:: log_command

   .. automethod:: log_output

   .. automethod:: log_error

   .. automethod:: load_banner

   .. automethod:: load_random_quote

Configuration Commands
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: src.cli.CryoDLShell.do_init

.. automethod:: src.cli.CryoDLShell.do_get

.. automethod:: src.cli.CryoDLShell.do_set

.. automethod:: src.cli.CryoDLShell.do_show

.. automethod:: src.cli.CryoDLShell.do_reset

.. automethod:: src.cli.CryoDLShell.do_export

.. automethod:: src.cli.CryoDLShell.do_import

Dependency Management Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: src.cli.CryoDLShell.do_add_dependency

.. automethod:: src.cli.CryoDLShell.do_list_dependencies

.. automethod:: src.cli.CryoDLShell.do_validate_dependencies

SLURM Commands
~~~~~~~~~~~~~~

.. automethod:: src.cli.CryoDLShell.do_slurm_show

.. automethod:: src.cli.CryoDLShell.do_slurm_update

.. automethod:: src.cli.CryoDLShell.do_slurm_generate

Software Integration Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: src.cli.CryoDLShell.do_model_angelo

.. automethod:: src.cli.CryoDLShell.do_topaz

.. automethod:: src.cli.CryoDLShell._run_topaz_preprocess

.. automethod:: src.cli.CryoDLShell._run_topaz_cross

Analysis Commands
~~~~~~~~~~~~~~~~

.. automethod:: src.cli.CryoDLShell.do_analyze_cv

.. automethod:: src.cli.CryoDLShell.do_fasta

Utility Commands
~~~~~~~~~~~~~~~

.. automethod:: src.cli.CryoDLShell.do_clear

.. automethod:: src.cli.CryoDLShell.do_pwd

.. automethod:: src.cli.CryoDLShell.do_ls

.. automethod:: src.cli.CryoDLShell.do_help

Exit Commands
~~~~~~~~~~~~

.. automethod:: src.cli.CryoDLShell.do_quit

.. automethod:: src.cli.CryoDLShell.do_exit

.. automethod:: src.cli.CryoDLShell.do_EOF

Topaz Analysis Module
--------------------

The :mod:`src.topaz_analysis` module provides analysis functions for Topaz results.

.. autofunction:: src.topaz_analysis.analyze_cross_validation

.. autofunction:: src.topaz_analysis.plot_training_curves

FASTA Sequence Builder
--------------------

The :class:`FastaBuilder` class provides functionality to fetch FASTA sequences from the RCSB PDB database.

.. autoclass:: src.build_fasta.FastaBuilder
   :members:
   :special-members: __init__

   .. automethod:: __init__

   .. automethod:: validate_pdb_id

   .. automethod:: fetch_pdb_info

   .. automethod:: fetch_polymer_entities

   .. automethod:: fetch_fasta_sequence

   .. automethod:: get_entity_info

   .. automethod:: build_fasta_from_pdb

   .. automethod:: build_fasta_from_multiple_pdbs

   .. automethod:: list_pdb_entities

Data Structures
--------------

Configuration Schema
~~~~~~~~~~~~~~~~~~~

The configuration is stored in JSON format with the following structure:

.. code-block:: json

   {
     "dependencies": {
       "topaz": {
         "path": "/usr/local/bin/topaz",
         "version": "0.2.5",
         "enabled": true
       },
       "model_angelo": {
         "path": "/opt/model-angelo/bin/model-angelo",
         "version": "1.0.1",
         "enabled": true
       }
     },
     "slurm": {
       "job_name": "cryodl_job",
       "nodes": 1,
       "ntasks": 1,
       "cpus_per_task": 4,
       "gres_gpu": 1,
       "time": "24:00:00",
       "mem": "16G",
       "partition": "notchpeak-gpu",
       "qos": "notchpeak-gpu",
       "account": "notchpeak-gpu",
       "output": "slurm-%j.out",
       "error": "slurm-%j.err"
     },
     "settings": {
       "max_threads": 8,
       "log_level": "INFO"
     },
     "paths": {
       "project_root": "/path/to/project",
       "data_dir": "/path/to/data",
       "output_dir": "/path/to/output"
     }
   }

Analysis Results
~~~~~~~~~~~~~~~

The :func:`analyze_cross_validation` function returns a dictionary with the following structure:

.. code-block:: python

   {
     'cv_results': pd.DataFrame,           # Full cross-validation results
     'cv_results_mean': pd.DataFrame,      # Mean results across folds
     'cv_results_epoch': pd.DataFrame,     # Best epoch results for each N
     'best_n': int,                        # Recommended N value
     'best_epoch': int,                    # Recommended number of epochs
     'best_auprc': float,                  # Best AUPRC achieved
     'recommendations': dict,              # Analysis recommendations
     'plots': dict,                        # Generated matplotlib figures
     'output_dir': str                     # Output directory path
   }

Error Handling
-------------

cryoDL uses Python's standard exception handling with custom error messages:

.. code-block:: python

   try:
       # Operation that might fail
       config_manager.validate_dependency_path("topaz")
   except FileNotFoundError:
       print("Topaz not found at configured path")
   except Exception as e:
       print(f"Unexpected error: {e}")

Common Exceptions
~~~~~~~~~~~~~~~~

- :class:`FileNotFoundError`: Dependency path not found
- :class:`ValueError`: Invalid configuration value
- :class:`KeyError`: Configuration key not found
- :class:`subprocess.CalledProcessError`: External command failed

Logging
-------

cryoDL uses Python's :mod:`logging` module for comprehensive logging:

.. code-block:: python

   import logging

   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('cryodl.log'),
           logging.StreamHandler()
       ]
   )

Log Levels
~~~~~~~~~~

- **INFO**: Normal operations, commands executed
- **WARNING**: Non-critical issues, missing dependencies
- **ERROR**: Command failures, configuration errors
- **DEBUG**: Detailed debugging information

Environment Variables
--------------------

cryoDL recognizes the following environment variables:

.. code-block:: bash

   export CRYODL_CONFIG_PATH="/path/to/config.json"  # Custom config path
   export CRYODL_LOG_LEVEL="DEBUG"                   # Set log level
   export CRYODL_LOG_FILE="/path/to/cryodl.log"      # Custom log file

Command Line Interface
---------------------

The main entry point for the CLI is the :func:`src.cli.main` function:

.. autofunction:: src.cli.main

Command Line Arguments
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cryodl [--log-file LOG_FILE] [--help]

- ``--log-file``: Specify custom log file path
- ``--help``: Show help message

Interactive Shell Features
-------------------------

The interactive shell provides several features:

Command History
~~~~~~~~~~~~~~

- Use arrow keys to navigate command history
- Tab completion for commands and file paths
- Command history persistence across sessions

Auto-completion
~~~~~~~~~~~~~~

The shell supports tab completion for:

- Built-in commands
- File and directory paths
- Configuration keys
- Dependency names

Error Recovery
~~~~~~~~~~~~~

- Graceful handling of invalid commands
- Detailed error messages with suggestions
- Automatic logging of all errors
- Session recovery after errors

Examples
--------

Basic Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.config_manager import ConfigManager

   # Initialize configuration manager
   config = ConfigManager()

   # Create default configuration
   config.create_default_config()

   # Add dependency
   config.update_dependency_path("topaz", "/usr/local/bin/topaz", "0.2.5")

   # Validate dependency
   if config.validate_dependency_path("topaz"):
       print("Topaz is properly configured")

   # Get configuration value
   topaz_path = config.get("dependencies.topaz.path")

   # Set configuration value
   config.set("settings.max_threads", 16)

Running Analysis
~~~~~~~~~~~~~~~

.. code-block:: python

   from src.topaz_analysis import analyze_cross_validation

   # Analyze cross-validation results
   results = analyze_cross_validation(
       cv_dir="saved_models/EMPIAR-10025/cv",
       n_values=[250, 300, 350, 400, 450, 500],
       k_folds=5,
       output_dir="analysis_results",
       save_plots=True,
       show_plots=False
   )

   # Access results
   print(f"Best N: {results['best_n']}")
   print(f"Best epochs: {results['best_epoch']}")
   print(f"Best AUPRC: {results['best_auprc']:.4f}")

Custom CLI Commands
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.cli import CryoDLShell
   from src.config_manager import ConfigManager

   # Create custom shell
   config = ConfigManager()
   shell = CryoDLShell(config, "custom.log")

   # Add custom command
   def do_custom_command(self, arg):
       """Custom command example."""
       print(f"Custom command executed with: {arg}")

   # Add method to shell
   shell.do_custom_command = do_custom_command

   # Run shell
   shell.cmdloop()

SLURM Integration
~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.config_manager import ConfigManager

   config = ConfigManager()

   # Update SLURM configuration
   config.update_slurm_config(
       nodes=2,
       gres_gpu=2,
       time="48:00:00",
       mem="96G",
       partition="notchpeak-gpu"
   )

   # Generate SLURM header
   header = config.generate_slurm_header(
       job_name="my_job",
       nodes=4,
       gres_gpu=4
   )

   print(header)
