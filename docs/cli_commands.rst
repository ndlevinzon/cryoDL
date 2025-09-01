CLI Commands Reference
=====================

This page provides a comprehensive reference for all available commands in the cryoDL interactive shell.

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

.. automethod:: src.cli.CryoDLShell._run_topaz_denoise

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

.. automethod:: src.cli.CryoDLShell.do_version

Exit Commands
~~~~~~~~~~~~

.. automethod:: src.cli.CryoDLShell.do_quit

.. automethod:: src.cli.CryoDLShell.do_exit

.. automethod:: src.cli.CryoDLShell.do_EOF

Command Examples
---------------

Complete Workflow Example
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start cryoDL
   cryodl

   # Initialize configuration
   cryoDL> init

   # Add dependencies
   cryoDL> add_dependency topaz /usr/local/bin/topaz 0.2.5
   cryoDL> add_dependency model_angelo /opt/model-angelo/bin/model-angelo

   # Validate dependencies
   cryoDL> validate_dependencies

   # Configure SLURM
   cryoDL> slurm_update --partition notchpeak-gpu --mem 96G --time 24:00:00

   # Run Topaz preprocessing
   cryoDL> topaz preprocess --local
   # Enter prompts...

   # Run cross-validation
   cryoDL> topaz cross --local
   # Enter prompts...

   # Run denoising workflow
   cryoDL> topaz denoise --local
   # Enter prompts...

   # Analyze results
   cryoDL> analyze_cv output_dir/saved_models/cv

   # Exit
   cryoDL> quit

Configuration Management Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # View current configuration
   cryoDL> show

   # Get specific values
   cryoDL> get dependencies.topaz.path
   cryoDL> get slurm.nodes

   # Update settings
   cryoDL> set settings.max_threads 16
   cryoDL> set slurm.time "48:00:00"

   # Export configuration
   cryoDL> export my_config.json

   # Import configuration
   cryoDL> import backup_config.json

SLURM Management Example
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # View SLURM settings
   cryoDL> slurm_show

   # Update SLURM configuration
   cryoDL> slurm_update --nodes 4 --gres-gpu 4 --time 48:00:00

   # Generate SLURM header
   cryoDL> slurm_generate --job-name my_job --output job.slurm

   # Submit jobs
   cryoDL> topaz preprocess
   cryoDL> model_angelo

Command Line Options
-------------------

Global Options
~~~~~~~~~~~~~

.. code-block:: bash

   cryodl --log-file my.log  # Use custom log file
   cryodl --help             # Show help

Environment Variables
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   export CRYODL_CONFIG_PATH=/path/to/config.json  # Custom config path
   export CRYODL_LOG_LEVEL=DEBUG                   # Set log level

Logging
-------

All commands and their outputs are automatically logged to `cryodl.log` in the current directory. The log includes:

- Command execution timestamps
- Input parameters
- Output messages
- Error messages
- Session information

Example log entry:

.. code-block:: text

   2024-01-15 10:30:45 - INFO - Command: topaz preprocess --local
   2024-01-15 10:30:45 - INFO - Output: Running Topaz preprocess locally
   2024-01-15 10:30:46 - INFO - Output: Topaz preprocess completed successfully
