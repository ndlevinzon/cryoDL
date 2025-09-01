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

This will likely take several hours to complete, depending on the size of your map and the resources allocated. Once the job is finished, you will find the output files in the specified output directory.

Step 3: Analyzing the Results
--------------------------

Continue with additional steps as needed.

**Interactive prompts:**

If the command prompts for input, show the interaction:

.. code-block:: bash

   cryoDL> topaz preprocess --local
   Enter path to micrographs: /path/to/micrographs
   Enter path to particles file: /path/to/particles.txt
   Enter output directory: output_dir
   Enter pixel size: 1.0

**File structure created:**

Show what files and directories should be created:

.. code-block:: text

   output_dir/
   ├── preprocessed/
   │   ├── micrographs.mrcs
   │   └── particles.txt
   ├── logs/
   │   └── preprocessing.log
   └── config.json

Verification
-----------

How to verify that everything worked correctly:

.. code-block:: bash

   # Check that files were created
   cryoDL> ls output_dir/

   # Validate the results
   cryoDL> [validation command]

**Expected verification output:**

.. code-block:: text

   [Show what successful verification looks like]

Advanced Options
---------------

Optional advanced configurations or variations:

.. code-block:: bash

   # Advanced option 1
   cryoDL> [command] --advanced-flag

   # Advanced option 2
   cryoDL> [command] --custom-parameter value

**When to use advanced options:**

Explain when and why you might want to use these advanced features.

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

**Practice Exercises:**

Optional exercises to reinforce learning:

1. **Exercise 1**: [Description of practice exercise]
   * Try [specific task]
   * Expected outcome: [what should happen]

2. **Exercise 2**: [Another practice exercise]
   * Try [specific task]
   * Expected outcome: [what should happen]

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

---

.. note::
   **Template Usage**: When creating a new tutorial from this template:

   1. Copy this file and rename it to ``tutorial_[topic].rst``
   2. Replace all placeholder text in [brackets] with actual content
   3. Remove any sections that aren't relevant to your tutorial
   4. Add the tutorial to the main documentation index
   5. Test all commands and examples to ensure they work correctly

**Template Sections to Customize:**

* **Title and Description**: Replace with your tutorial's specific topic
* **Prerequisites**: List what users need before starting
* **Learning Objectives**: What users will learn
* **Steps**: Replace with your actual tutorial steps
* **Commands**: Use real cryoDL commands with actual examples
* **Output**: Show real expected output
* **Troubleshooting**: Address common issues for your specific topic
* **Next Steps**: Link to relevant documentation
