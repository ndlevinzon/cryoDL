Tutorial 1: Using Model-Angelo with cryoDL FastaBuilder
================

In this tutorial, we will walk through the process of using the Model-Angelo tool integrated within cryoDL to build and refine protein structures from cryo-EM maps.

.. note::
   Model-Angelo is a powerful stand-alone tool for automated model building and refinement. This tutorial will guide you through its integration with cryoDL, allowing for streamlined workflows in structural biology. Please refer to the official Model-Angelo citation and documentation for more detailed information on its capabilities and usage.


------------

Before starting this tutorial, make sure you have:

* cryoDL installed and configured (see :ref:`installation`)
* Have Model-Angelo installed (see `Model-Angelo GitHub)
* Access to cryo-EM maps (.mrc) and corresponding sequence data (PDB or UniProt IDs)

Learning Objectives
------------------

By the end of this tutorial, you will be able to:

* Build FASTA files using cryoDL's FastaBuilder, using either PDB or UniProt IDs
* Run Model-Angelo through cryoDL to generate protein models from cryo-EM maps
* Annotate the generated models with sequence information

Step 1: Building a FASTA File
--------------------------

Before running Model-Angelo, you need to create a FASTA file containing the sequences of the proteins you want to model. You can do this using cryoDL's FastaBuilder.

First, CD into the directory containing your Cryo-EM maps. We will build our FASTA at this same directory.

**Using the command line:**

.. code-block:: bash

   $ cd /path/to/your/cryoem/maps.mrc

We are now in the directory where our cryo-EM maps are located. This is important because we will be running Model-Angelo in this directory later.

Next, we will launch cryoDL and use the FastaBuilder command to create a FASTA file. You can provide either PDB IDs or UniProt IDs. In this example, we will use both methods with the --multiple flag.

**Using the command line:**

.. code-block:: text

    $ cryoDL
    cryoDL> fasta --multiple 1A2B X1Y2B3
    INFO:cryodl_interactive:Command: fasta --multiple 1A2B X1Y2B3
    Processing multiple identifiers: 1A2B, X1Y2B3
    Output file: combined_protein.fasta
    INFO:src.build_fasta:Processing PDB ID: 1A2B
    INFO:src.build_fasta:Processing UniProt ID: X1Y2B3
    Successfully created FASTA file: combined_protein.fasta | Successfully processed: PDB:1A2B, UniProt:X1Y2B3
    INFO:cryodl_interactive:Output: Successfully created FASTA file: combined_protein.fasta

We now have a FASTA file named `combined_protein.fasta` in our current directory, which contains the sequences for the proteins with PDB ID 4B2T and UniProt ID Q8N3Y1.

Step 2: Running Model-Angelo
---------------------------

Once you have your FASTA file ready, you can run Model-Angelo to build models from your cryo-EM maps.

**Using the cryoDL command line:**

.. code-block:: text

    cryoDL> model-angelo
    INFO:cryodl_interactive:Command: model_angelo
    ModelAngelo Setup:
    --------------------
    Enter path to .mrc file: /path/to/your/cryoem/maps.mrc
    Enter path to protein FASTA file: /path/to/your/cryoem/combined_protein.fasta

    Job Summary:
        Job Name: model_angelo_maps
        MRC File: /path/to/your/cryoem/maps.mrc
        FASTA File: /path/to/your/cryoem/combined_protein.fasta
        Output Directory: model_angelo_output_maps
        SLURM Script: model_angelo_maps.slurm
        Time Limit: 06:00:00
        Nodes: 1
        CPUs per Task: 4
        Memory: 96G
        GPUs: 1
        Partition: notchpeak-gpu

        Submit this job to SLURM? (Y/N):

**What these do:**

After inputting the required information, cryoDL summarizes the job details, including the paths to the MRC file and FASTA file, output directory, SLURM script name, and resource allocations. You can change any of these parameters in the configuration file if needed.
You will be prompted to confirm submission to SLURM. You can also choose not to submit the job immediately by entering 'N', in which case the SLURM script will be saved for later submission, or run model-angelo locally with the --local flag (not recommended, as you will likely need more memory than is available by default).

**Using the cryoDL command line:**

.. code-block:: text

    Submit this job to SLURM? (Y/N): y
    ModelAngelo job submitted successfully. Job ID: 5976006
    INFO:cryodl_interactive:Output: ModelAngelo job submitted successfully. Job ID: 5976006
    SLURM script saved as: model_angelo_maps.slurm
    Job output will be in: model_angelo_maps_<job_id>.out
    Job errors will be in: model_angelo_maps_<job_id>.err

**Expected results:**

This will likely take several hours to complete, depending on the size of your map and the resources allocated. You can see the status of the Model-Angelo job in the .out file, and any errors will be printed to the .err file. Once the job is finished, you will find the output files in the specified output directory.

Step 3: Analyzing the Results
--------------------------

Once completed, navigate to the output directory specified during the Model-Angelo setup. You should find several files, including:

.. code-block:: text

   /path/to/your/cryoem/maps/
        ├── see_alpa_output/                         # SEE-Alpha stage: point detections from density
        │   ├── see_alpha_output_p.cif               # Predicted phosphate (P) points for NA backbones (RNA/DNA “seed” positions)
        │   ├── see_alpha_output_ca.cif              # Predicted C-alpha (CA) points for protein backbones (“seed” positions)
        │   ├── see_alpha_merged_output.cif          # Combined/filtered union of the P + Cα point clouds used to start tracing
        │   ├── output_p_points_before_pruning.cif   # Raw P detections BEFORE pruning/thinning (contains extra/spurious points)
        │   └── output_ca_points_before_pruning.cif  # Raw Cα detections BEFORE pruning/thinning (more false positives)
        ├── gnn_output_round_1/                      # Round 1 graph-neural-network (GNN) inference:
        │                                            #   intermediate graphs, per-point residue/base-type probabilities,
        │                                            #   tentative chain segments, and early sequence assignments
        ├── gnn_output_round_2/                      # Round 2 GNN inference: improved graphs, tentative chain segments, and sequence assignments
        ├── gnn_output_round_3/                      # Round 3 GNN inference: final graphs, chain segments, and sequence assignments
        ├── model_angelo_output_map_raw.cif          # First-pass built model from GNN tracing (may be poly-Ala/UNK in places;
        │                                            #   pre–HMM/sequence-identification or before final rebuild/cleanup)
        ├── model_angelo_output_map.cif              # Final rebuilt/cleaned-up model from GNN tracing (may be poly-Ala/UNK in places;
        │                                            #   this is the file you typically inspect, refine, and deposit
        └── model_angelo.log                         # Full run log: versions, parameters, timings, warnings/errors (keep for repro)

We can visualize the final model (model_angelo_output_map.cif) using molecular visualization software like PyMOL or ChimeraX.
In order to annotate which chains correspond to which sequences in our FASTA file, we can use the --annotate flag in cryoDL.

**Using the command line:**

.. code-block:: text

    $ cd /path/to/your/cryoem/maps/
    $ cryoDL

**Using the CryoDL command line:**

.. code-block:: text

    cryoDL> fasta --annotate model_angelo_output_map.cif ../combined_protein.fasta
    INFO:cryodl_interactive:Command: fasta --annotate model_angelo_output_map.cif ../combined_protein.fasta
    Creating annotated sequence from CIF: model_angelo_output_map.cif
    Using FASTA file: ../combined_protein.fasta
    Output file: annotations.csv
    Successfully created annotated sequence file: annotations.csv
    INFO:cryodl_interactive:Output: Successfully created annotated FASTA file: annotations.csv

This will generate an (annotations.csv) file that maps the chains in your Model-Angelo output to the sequences in your FASTA file. You can open this CSV file in any spreadsheet software or text editor to view the annotations.

Troubleshooting
--------------

Common issues and their solutions:

**Issue 1: [Common Problem]**

.. code-block:: text

   Error: [error message]

**Solution:**

.. code-block:: bash

   # Fix command
   cryoDL> [fix command]

**Issue 2: [Another Common Problem]**

.. code-block:: text

   Error: [error message]

**Solution:**

.. code-block:: bash

   # Fix command
   cryoDL> [fix command]

**Getting Help:**

If you're still having issues:

.. code-block:: bash

   # Get help for the command
   cryoDL> help [command_name]

   # Check the logs
   cryoDL> ls *.log

Next Steps
----------

What to do after completing this tutorial:

* [Link to related tutorial or documentation]
* [Link to advanced usage guide]
* [Link to troubleshooting guide]

**Related Documentation:**

* :ref:`cli_commands` - Complete command reference
* :ref:`api_reference` - Python API documentation
* :ref:`configuration` - Configuration options

Summary
-------

Brief summary of what was accomplished in this tutorial.

**Key takeaways:**

* [Key point 1]
* [Key point 2]
* [Key point 3]

**Commands learned:**

* ``[command1]`` - [what it does]
* ``[command2]`` - [what it does]
* ``[command3]`` - [what it does]

