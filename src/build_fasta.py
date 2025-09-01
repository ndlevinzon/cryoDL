#!/usr/bin/env python3
"""
FASTA sequence builder for cryoDL.

This module provides functionality to retrieve FASTA sequences from the RCSB PDB database
and UniProt database, and save them to indexed files for use in cryo-EM workflows.
"""

import os
import sys
import requests
import time
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Set up logging
logger = logging.getLogger(__name__)


class FastaBuilder:
    """Build FASTA files from PDB IDs or UniProt IDs by retrieving sequences from RCSB PDB and UniProt.

    This class provides methods to fetch FASTA sequences from the RCSB PDB database and UniProt database
    and save them to indexed files for use in cryo-EM software workflows.

    Attributes:
        rcsb_fasta_url (str): Base URL for RCSB PDB FASTA sequences
        uniprot_fasta_url (str): Base URL for UniProt FASTA sequences
        timeout (int): Request timeout in seconds
        max_retries (int): Maximum number of retry attempts for failed requests
        retry_delay (float): Delay between retry attempts in seconds
    """

    def __init__(
            self, timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0
    ):
        """Initialize the FastaBuilder.

        Args:
            timeout (int, optional): Request timeout in seconds. Defaults to 30.
            max_retries (int, optional): Maximum number of retry attempts for failed requests.
                Defaults to 3.
            retry_delay (float, optional): Delay between retry attempts in seconds.
                Defaults to 1.0.

        Example:
            builder = FastaBuilder(timeout=60, max_retries=5)
        """
        self.rcsb_fasta_url = "https://www.rcsb.org/fasta/entry"
        self.uniprot_fasta_url = "https://rest.uniprot.org/uniprotkb"
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def validate_pdb_id(self, pdb_id: str) -> bool:
        """Validate a PDB ID format.

        PDB IDs should be 4 characters long and contain only alphanumeric characters.

        Args:
            pdb_id (str): The PDB ID to validate.

        Returns:
            bool: True if the PDB ID is valid, False otherwise.

        Example:
            builder.validate_pdb_id("1ABC")
            True
            builder.validate_pdb_id("INVALID")
            False
        """
        if not pdb_id or len(pdb_id) != 4:
            return False

        # PDB IDs should contain only alphanumeric characters
        return pdb_id.isalnum()

    def validate_uniprot_id(self, uniprot_id: str) -> bool:
        """Validate a UniProt ID format.

        UniProt IDs follow specific patterns:
        - Entry names: 1-11 characters, alphanumeric and underscores
        - Accession numbers: 6-10 characters, alphanumeric, format like A0A0A0 or P12345

        Args:
            uniprot_id (str): The UniProt ID to validate.

        Returns:
            bool: True if the UniProt ID is valid, False otherwise.

        Example:
            builder.validate_uniprot_id("Q8N3Y1")
            True
            builder.validate_uniprot_id("P53_HUMAN")
            True
            builder.validate_uniprot_id("INVALID")
            False
        """
        if not uniprot_id:
            return False

        # UniProt accession number pattern (6-10 alphanumeric characters)
        accession_pattern = r'^[A-N,R-Z][0-9][A-Z][A-Z,0-9][A-Z,0-9][0-9]$|^[O,P,Q][0-9][A-Z,0-9][A-Z,0-9][A-Z,0-9][0-9]$|^[A-N,R-Z][0-9][A-Z][A-Z,0-9][A-Z,0-9][0-9][A-Z,0-9][A-Z,0-9][0-9]$|^[O,P,Q][0-9][A-Z,0-9][A-Z,0-9][A-Z,0-9][0-9][A-Z,0-9][A-Z,0-9][0-9]$'

        # UniProt entry name pattern (1-11 characters, alphanumeric and underscores)
        entry_pattern = r'^[A-Z0-9_]{1,11}$'

        return bool(re.match(accession_pattern, uniprot_id) or re.match(entry_pattern, uniprot_id))

    def get_id_type(self, identifier: str) -> str:
        """Determine if an identifier is a PDB ID or UniProt ID.

        Args:
            identifier (str): The identifier to classify.

        Returns:
            str: 'pdb' if it's a PDB ID, 'uniprot' if it's a UniProt ID, 'unknown' otherwise.

        Example:
            builder.get_id_type("2BG9")
            'pdb'
            builder.get_id_type("Q8N3Y1")
            'uniprot'
            builder.get_id_type("INVALID")
            'unknown'
        """
        if self.validate_pdb_id(identifier):
            return 'pdb'
        elif self.validate_uniprot_id(identifier):
            return 'uniprot'
        else:
            return 'unknown'

    def fetch_fasta_sequence(self, identifier: str) -> Optional[str]:
        """Fetch FASTA sequence for a PDB entry or UniProt entry using direct FASTA URL.

        Args:
            identifier (str): The PDB ID or UniProt ID to fetch FASTA sequence for.

        Returns:
            Optional[str]: FASTA sequence string, or None if failed.

        Example:
            sequence = builder.fetch_fasta_sequence("2BG9")
            if sequence:
                print(sequence[:100])  # First 100 characters
            sequence = builder.fetch_fasta_sequence("Q8N3Y1")
            if sequence:
                print(sequence[:100])  # First 100 characters
        """
        id_type = self.get_id_type(identifier)

        if id_type == 'pdb':
            return self._fetch_pdb_fasta_sequence(identifier)
        elif id_type == 'uniprot':
            return self._fetch_uniprot_fasta_sequence(identifier)
        else:
            logger.error(f"Invalid identifier format: {identifier}")
            return None

    def _fetch_pdb_fasta_sequence(self, pdb_id: str) -> Optional[str]:
        """Fetch FASTA sequence for a PDB entry using direct FASTA URL.

        Args:
            pdb_id (str): The PDB ID to fetch FASTA sequence for.

        Returns:
            Optional[str]: FASTA sequence string, or None if failed.
        """
        if not self.validate_pdb_id(pdb_id):
            logger.error(f"Invalid PDB ID format: {pdb_id}")
            return None

        url = f"{self.rcsb_fasta_url}/{pdb_id}"

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Return the FASTA content directly
                return response.text

            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for PDB {pdb_id}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to fetch FASTA sequence for PDB {pdb_id} after {self.max_retries} attempts"
                    )
                    return None

    def _fetch_uniprot_fasta_sequence(self, uniprot_id: str) -> Optional[str]:
        """Fetch FASTA sequence for a UniProt entry using REST API.

        Args:
            uniprot_id (str): The UniProt ID to fetch FASTA sequence for.

        Returns:
            Optional[str]: FASTA sequence string, or None if failed.
        """
        if not self.validate_uniprot_id(uniprot_id):
            logger.error(f"Invalid UniProt ID format: {uniprot_id}")
            return None

        url = f"{self.uniprot_fasta_url}/{uniprot_id}.fasta"

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Return the FASTA content directly
                return response.text

            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for UniProt {uniprot_id}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to fetch FASTA sequence for UniProt {uniprot_id} after {self.max_retries} attempts"
                    )
                    return None

    def build_fasta_from_pdb(
            self, pdb_id: str, output_file: str = None
    ) -> Tuple[bool, str]:
        """Build a FASTA file from a single PDB ID.

        Args:
            pdb_id (str): The PDB ID to fetch sequences from.
            output_file (str, optional): Output file path. If None, uses default naming.

        Returns:
            Tuple[bool, str]: (success, message) indicating operation result.

        Example:
            success, message = builder.build_fasta_from_pdb("2BG9", "protein.fasta")
            print(message)
        """
        if not self.validate_pdb_id(pdb_id):
            return False, f"Invalid PDB ID format: {pdb_id}"

        # Generate output filename if not provided
        if output_file is None:
            output_file = f"{pdb_id}_protein.fasta"

        # Fetch FASTA sequence
        fasta_content = self._fetch_pdb_fasta_sequence(pdb_id)
        if not fasta_content:
            return False, f"Failed to fetch FASTA sequence for PDB ID: {pdb_id}"

        try:
            # Write FASTA content directly to file
            with open(output_file, "w") as f:
                f.write(fasta_content)

            return True, f"Successfully created FASTA file: {output_file}"

        except Exception as e:
            logger.error(f"Error writing FASTA file: {e}")
            return False, f"Error writing FASTA file: {e}"

    def build_fasta_from_uniprot(
            self, uniprot_id: str, output_file: str = None
    ) -> Tuple[bool, str]:
        """Build a FASTA file from a single UniProt ID.

        Args:
            uniprot_id (str): The UniProt ID to fetch sequences from.
            output_file (str, optional): Output file path. If None, uses default naming.

        Returns:
            Tuple[bool, str]: (success, message) indicating operation result.

        Example:
            success, message = builder.build_fasta_from_uniprot("Q8N3Y1", "protein.fasta")
            print(message)
        """
        if not self.validate_uniprot_id(uniprot_id):
            return False, f"Invalid UniProt ID format: {uniprot_id}"

        # Generate output filename if not provided
        if output_file is None:
            output_file = f"{uniprot_id}_protein.fasta"

        # Fetch FASTA sequence
        fasta_content = self._fetch_uniprot_fasta_sequence(uniprot_id)
        if not fasta_content:
            return False, f"Failed to fetch FASTA sequence for UniProt ID: {uniprot_id}"

        try:
            # Write FASTA content directly to file
            with open(output_file, "w") as f:
                f.write(fasta_content)

            return True, f"Successfully created FASTA file: {output_file}"

        except Exception as e:
            logger.error(f"Error writing FASTA file: {e}")
            return False, f"Error writing FASTA file: {e}"

    def build_fasta_from_identifier(
            self, identifier: str, output_file: str = None
    ) -> Tuple[bool, str]:
        """Build a FASTA file from a single identifier (PDB ID or UniProt ID).

        Args:
            identifier (str): The PDB ID or UniProt ID to fetch sequences from.
            output_file (str, optional): Output file path. If None, uses default naming.

        Returns:
            Tuple[bool, str]: (success, message) indicating operation result.

        Example:
            success, message = builder.build_fasta_from_identifier("2BG9", "protein.fasta")
            print(message)
            success, message = builder.build_fasta_from_identifier("Q8N3Y1", "protein.fasta")
            print(message)
        """
        id_type = self.get_id_type(identifier)

        if id_type == 'pdb':
            return self.build_fasta_from_pdb(identifier, output_file)
        elif id_type == 'uniprot':
            return self.build_fasta_from_uniprot(identifier, output_file)
        else:
            return False, f"Invalid identifier format: {identifier} (not a valid PDB ID or UniProt ID)"

    def build_fasta_from_multiple_pdbs(
            self, pdb_ids: List[str], output_file: str = "combined_protein.fasta"
    ) -> Tuple[bool, str]:
        """Build a FASTA file from multiple PDB IDs.

        Args:
            pdb_ids (List[str]): List of PDB IDs to fetch sequences from.
            output_file (str, optional): Output file path. Defaults to "combined_protein.fasta".

        Returns:
            Tuple[bool, str]: (success, message) indicating operation result.

        Example:
            pdb_list = ["1ABC", "2DEF", "3GHI"]
            success, message = builder.build_fasta_from_multiple_pdbs(pdb_list, "my_proteins.fasta")
            print(message)
        """
        if not pdb_ids:
            return False, "No PDB IDs provided"

        # Validate all PDB IDs
        invalid_ids = [pdb_id for pdb_id in pdb_ids if not self.validate_pdb_id(pdb_id)]
        if invalid_ids:
            return False, f"Invalid PDB ID(s): {', '.join(invalid_ids)}"

        successful_pdbs = []
        failed_pdbs = []

        try:
            with open(output_file, "w") as f:
                for pdb_id in pdb_ids:
                    logger.info(f"Processing PDB ID: {pdb_id}")

                    # Fetch FASTA sequence
                    fasta_content = self._fetch_pdb_fasta_sequence(pdb_id)
                    if fasta_content:
                        # Write FASTA content to file
                        f.write(fasta_content)
                        f.write("\n")  # Add separator between entries
                        successful_pdbs.append(pdb_id)
                    else:
                        failed_pdbs.append(f"{pdb_id} (failed to fetch)")

            # Prepare result message
            message_parts = [f"Successfully created FASTA file: {output_file}"]
            if successful_pdbs:
                message_parts.append(
                    f"Successfully processed: {', '.join(successful_pdbs)}"
                )
            if failed_pdbs:
                message_parts.append(f"Failed to process: {', '.join(failed_pdbs)}")

            success = len(successful_pdbs) > 0
            return success, " | ".join(message_parts)

        except Exception as e:
            logger.error(f"Error writing combined FASTA file: {e}")
            return False, f"Error writing combined FASTA file: {e}"

    def build_fasta_from_multiple_identifiers(
            self, identifiers: List[str], output_file: str = "combined_protein.fasta"
    ) -> Tuple[bool, str]:
        """Build a FASTA file from multiple identifiers (PDB IDs and/or UniProt IDs).

        Args:
            identifiers (List[str]): List of PDB IDs and/or UniProt IDs to fetch sequences from.
            output_file (str, optional): Output file path. Defaults to "combined_protein.fasta".

        Returns:
            Tuple[bool, str]: (success, message) indicating operation result.

        Example:
            id_list = ["2BG9", "Q8N3Y1", "1ABC", "P53_HUMAN"]
            success, message = builder.build_fasta_from_multiple_identifiers(id_list, "my_proteins.fasta")
            print(message)
        """
        if not identifiers:
            return False, "No identifiers provided"

        # Validate all identifiers
        invalid_ids = []
        pdb_ids = []
        uniprot_ids = []

        for identifier in identifiers:
            id_type = self.get_id_type(identifier)
            if id_type == 'pdb':
                pdb_ids.append(identifier)
            elif id_type == 'uniprot':
                uniprot_ids.append(identifier)
            else:
                invalid_ids.append(identifier)

        if invalid_ids:
            return False, f"Invalid identifier(s): {', '.join(invalid_ids)}"

        successful_ids = []
        failed_ids = []

        try:
            with open(output_file, "w") as f:
                # Process PDB IDs
                for pdb_id in pdb_ids:
                    logger.info(f"Processing PDB ID: {pdb_id}")
                    fasta_content = self._fetch_pdb_fasta_sequence(pdb_id)
                    if fasta_content:
                        f.write(fasta_content)
                        f.write("\n")  # Add separator between entries
                        successful_ids.append(f"PDB:{pdb_id}")
                    else:
                        failed_ids.append(f"PDB:{pdb_id} (failed to fetch)")

                # Process UniProt IDs
                for uniprot_id in uniprot_ids:
                    logger.info(f"Processing UniProt ID: {uniprot_id}")
                    fasta_content = self._fetch_uniprot_fasta_sequence(uniprot_id)
                    if fasta_content:
                        f.write(fasta_content)
                        f.write("\n")  # Add separator between entries
                        successful_ids.append(f"UniProt:{uniprot_id}")
                    else:
                        failed_ids.append(f"UniProt:{uniprot_id} (failed to fetch)")

            # Prepare result message
            message_parts = [f"Successfully created FASTA file: {output_file}"]
            if successful_ids:
                message_parts.append(
                    f"Successfully processed: {', '.join(successful_ids)}"
                )
            if failed_ids:
                message_parts.append(f"Failed to process: {', '.join(failed_ids)}")

            success = len(successful_ids) > 0
            return success, " | ".join(message_parts)

        except Exception as e:
            logger.error(f"Error writing combined FASTA file: {e}")
            return False, f"Error writing combined FASTA file: {e}"

    def create_annotated_sequence(
            self,
            cif_file: str,
            fasta_file: str,
            output_file: str = "annotated_sequence.fasta"
    ) -> Tuple[bool, str]:
        """Create an annotated FASTA file that aligns FASTA sequences to CIF subunits.

        This function takes a ModelAngelo output .cif file and a FASTA file, then creates
        an annotated sequence file that maps the FASTA sequence names to the corresponding
        subunits in the .cif file.

        Args:
            cif_file (str): Path to the ModelAngelo output .cif file
            fasta_file (str): Path to the input FASTA file
            output_file (str, optional): Output file name. Defaults to "annotated_sequence.fasta".

        Returns:
            Tuple[bool, str]: (success, message) where success is True if the operation
                completed successfully, False otherwise. Message contains details about
                the operation result.

        Example:
            success, message = builder.create_annotated_sequence(
                "modelangelo_output.cif",
                "input_sequences.fasta",
                "annotated_sequences.fasta"
            )
        """
        try:
            # Validate input files
            if not os.path.exists(cif_file):
                return False, f"Error: CIF file not found: {cif_file}"

            if not os.path.exists(fasta_file):
                return False, f"Error: FASTA file not found: {fasta_file}"

            # Read and parse the CIF file
            cif_data = self._parse_cif_file(cif_file)
            if not cif_data:
                return False, f"Error: Failed to parse CIF file: {cif_file}"

            # Read and parse the FASTA file
            fasta_data = self._parse_fasta_file(fasta_file)
            if not fasta_data:
                return False, f"Error: Failed to parse FASTA file: {fasta_file}"

            # Create annotated sequences
            annotated_sequences = self._create_annotations(cif_data, fasta_data)

            # Write the annotated sequences to output file
            self._write_annotated_sequences(annotated_sequences, output_file)

            return True, f"Successfully created annotated sequence file: {output_file}"

        except Exception as e:
            logger.error(f"Error creating annotated sequence: {str(e)}")
            return False, f"Error: {str(e)}"

    def _parse_cif_file(self, cif_file: str) -> Optional[Dict]:
        """Parse a CIF file and extract sequence information.

        Args:
            cif_file (str): Path to the CIF file

        Returns:
            Optional[Dict]: Dictionary containing parsed CIF data, or None if failed
        """
        try:
            cif_data = {
                'entities': {},
                'sequences': {},
                'chains': {}
            }

            with open(cif_file, 'r') as f:
                lines = f.readlines()

            current_section = None
            current_entity = None

            for line in lines:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Check for section headers
                if line.startswith('_entity.'):
                    current_section = 'entity'
                    current_entity = line.split('.')[1]
                    if current_entity not in cif_data['entities']:
                        cif_data['entities'][current_entity] = {}
                elif line.startswith('_entity_poly_seq.'):
                    current_section = 'sequence'
                elif line.startswith('_atom_site.'):
                    current_section = 'atoms'

                # Parse entity information
                if current_section == 'entity' and current_entity:
                    if line.startswith('_entity.'):
                        key = line.split('.')[1]
                        cif_data['entities'][current_entity][key] = None
                    elif line and not line.startswith('_'):
                        # This is a value line
                        if current_entity in cif_data['entities']:
                            # Find the last key that doesn't have a value
                            for key in cif_data['entities'][current_entity]:
                                if cif_data['entities'][current_entity][key] is None:
                                    cif_data['entities'][current_entity][key] = line
                                    break

                # Parse sequence information
                if current_section == 'sequence':
                    if line.startswith('_entity_poly_seq.'):
                        key = line.split('.')[1]
                        if key not in cif_data['sequences']:
                            cif_data['sequences'][key] = []
                    elif line and not line.startswith('_'):
                        # This is a sequence data line
                        parts = line.split()
                        if len(parts) >= 3:  # entity_id, seq_id, res_name
                            entity_id = parts[0]
                            seq_id = parts[1]
                            res_name = parts[2]

                            if entity_id not in cif_data['sequences']:
                                cif_data['sequences'][entity_id] = []

                            cif_data['sequences'][entity_id].append({
                                'seq_id': seq_id,
                                'res_name': res_name
                            })

            return cif_data

        except Exception as e:
            logger.error(f"Error parsing CIF file: {str(e)}")
            return None

    def _parse_fasta_file(self, fasta_file: str) -> Optional[Dict]:
        """Parse a FASTA file and extract sequence information.

        Args:
            fasta_file (str): Path to the FASTA file

        Returns:
            Optional[Dict]: Dictionary containing parsed FASTA data, or None if failed
        """
        try:
            fasta_data = {}

            with open(fasta_file, 'r') as f:
                lines = f.readlines()

            current_header = None
            current_sequence = []

            for line in lines:
                line = line.strip()

                if line.startswith('>'):
                    # Save previous sequence if exists
                    if current_header and current_sequence:
                        fasta_data[current_header] = ''.join(current_sequence)

                    # Start new sequence
                    current_header = line[1:]  # Remove '>' character
                    current_sequence = []
                elif line and current_header:
                    current_sequence.append(line)

            # Save the last sequence
            if current_header and current_sequence:
                fasta_data[current_header] = ''.join(current_sequence)

            return fasta_data

        except Exception as e:
            logger.error(f"Error parsing FASTA file: {str(e)}")
            return None

    def _create_annotations(self, cif_data: Dict, fasta_data: Dict) -> List[Dict]:
        """Create annotations by matching CIF entities to FASTA sequences.

        Args:
            cif_data (Dict): Parsed CIF data
            fasta_data (Dict): Parsed FASTA data

        Returns:
            List[Dict]: List of annotated sequences
        """
        annotated_sequences = []

        # For each entity in the CIF file, try to find a matching FASTA sequence
        for entity_id, entity_info in cif_data['entities'].items():
            entity_type = entity_info.get('type', '')

            # Only process polymer entities (proteins, nucleic acids)
            if entity_type in ['polymer', 'polypeptide(L)', 'polyribonucleotide', 'polydeoxyribonucleotide']:

                # Get the sequence from CIF
                cif_sequence = self._get_cif_sequence(cif_data, entity_id)

                # Try to find a matching FASTA sequence
                matched_fasta = self._find_matching_fasta(cif_sequence, fasta_data)

                if matched_fasta:
                    annotated_sequences.append({
                        'entity_id': entity_id,
                        'entity_type': entity_type,
                        'entity_title': entity_info.get('pdbx_description', 'Unknown'),
                        'cif_sequence': cif_sequence,
                        'fasta_header': matched_fasta,
                        'fasta_sequence': fasta_data[matched_fasta]
                    })
                else:
                    # If no match found, create annotation with just CIF data
                    annotated_sequences.append({
                        'entity_id': entity_id,
                        'entity_type': entity_type,
                        'entity_title': entity_info.get('pdbx_description', 'Unknown'),
                        'cif_sequence': cif_sequence,
                        'fasta_header': None,
                        'fasta_sequence': None
                    })

        return annotated_sequences

    def _get_cif_sequence(self, cif_data: Dict, entity_id: str) -> str:
        """Extract the amino acid sequence for a given entity from CIF data.

        Args:
            cif_data (Dict): Parsed CIF data
            entity_id (str): Entity ID to extract sequence for

        Returns:
            str: Amino acid sequence as one-letter codes
        """
        if entity_id not in cif_data['sequences']:
            return ""

        # Amino acid three-letter to one-letter code mapping
        aa_mapping = {
            'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
            'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
            'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
            'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
            'SEC': 'U', 'PYL': 'O'  # Selenocysteine and Pyrrolysine
        }

        sequence = []
        for residue in cif_data['sequences'][entity_id]:
            res_name = residue['res_name']
            if res_name in aa_mapping:
                sequence.append(aa_mapping[res_name])
            else:
                sequence.append('X')  # Unknown amino acid

        return ''.join(sequence)

    def _find_matching_fasta(self, cif_sequence: str, fasta_data: Dict) -> Optional[str]:
        """Find a FASTA sequence that matches the CIF sequence.

        Args:
            cif_sequence (str): Sequence from CIF file
            fasta_data (Dict): Parsed FASTA data

        Returns:
            Optional[str]: Matching FASTA header, or None if no match found
        """
        if not cif_sequence:
            return None

        # Try exact matches first
        for header, sequence in fasta_data.items():
            if sequence == cif_sequence:
                return header

        # Try partial matches (if CIF sequence is shorter)
        for header, sequence in fasta_data.items():
            if cif_sequence in sequence or sequence in cif_sequence:
                return header

        return None

    def _write_annotated_sequences(self, annotated_sequences: List[Dict], output_file: str):
        """Write annotated sequences to output file.

        Args:
            annotated_sequences (List[Dict]): List of annotated sequences
            output_file (str): Output file path
        """
        with open(output_file, 'w') as f:
            for i, annotation in enumerate(annotated_sequences, 1):
                # Write header with entity information
                f.write(
                    f">Entity_{annotation['entity_id']} | {annotation['entity_type']} | {annotation['entity_title']}\n")

                # Write the sequence (prefer FASTA sequence if available, otherwise CIF sequence)
                sequence = annotation['fasta_sequence'] or annotation['cif_sequence']
                if sequence:
                    # Write sequence in 80-character lines
                    for j in range(0, len(sequence), 80):
                        f.write(sequence[j:j + 80] + '\n')

                f.write('\n')  # Add blank line between sequences


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Build FASTA files from PDB IDs")
    parser.add_argument("pdb_ids", nargs="+", help="PDB IDs to process")
    parser.add_argument("-o", "--output", help="Output file name")
    parser.add_argument("--multiple", action="store_true", help="Combine multiple PDB IDs into one file")
    parser.add_argument("--annotate", action="store_true", help="Create annotated sequences from CIF and FASTA files")
    parser.add_argument("--cif-file", help="CIF file for annotation (required with --annotate)")
    parser.add_argument("--fasta-file", help="FASTA file for annotation (required with --annotate)")

    args = parser.parse_args()

    builder = FastaBuilder()

    if args.annotate:
        if not args.cif_file or not args.fasta_file:
            print("Error: --cif-file and --fasta-file are required with --annotate")
            sys.exit(1)

        success, message = builder.create_annotated_sequence(
            args.cif_file, args.fasta_file, args.output or "annotated_sequence.fasta"
        )
        print(message)
        sys.exit(0 if success else 1)

    if args.multiple or len(args.pdb_ids) > 1:
        success, message = builder.build_fasta_from_multiple_pdbs(
            args.pdb_ids, args.output
        )
    else:
        success, message = builder.build_fasta_from_pdb(
            args.pdb_ids[0], args.output
        )

    print(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
