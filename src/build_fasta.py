#!/usr/bin/env python3
"""
FASTA sequence builder for cryoDL.

This module provides functionality to retrieve FASTA sequences from the RCSB PDB database
and save them to indexed files for use in cryo-EM workflows.
"""

import os
import sys
import requests
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin
import logging

# Set up logging
logger = logging.getLogger(__name__)


class FastaBuilder:
    """Build FASTA files from PDB IDs by retrieving sequences from RCSB PDB.

    This class provides methods to fetch FASTA sequences from the RCSB PDB database
    and save them to indexed files for use in cryo-EM software workflows.

    Attributes:
        rcsb_base_url (str): Base URL for RCSB PDB API
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
        self.rcsb_base_url = "https://data.rcsb.org/rest/v1/core"
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

    def fetch_pdb_info(self, pdb_id: str) -> Optional[Dict]:
        """Fetch basic information about a PDB entry.

        Args:
            pdb_id (str): The PDB ID to fetch information for.

        Returns:
            Optional[Dict]: Dictionary containing PDB information, or None if failed.

        Example:
            info = builder.fetch_pdb_info("1ABC")
            print(info.get("title", "No title available"))
        """
        if not self.validate_pdb_id(pdb_id):
            logger.error(f"Invalid PDB ID format: {pdb_id}")
            return None

        url = f"{self.rcsb_base_url}/entry/{pdb_id}"

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {pdb_id}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to fetch PDB info for {pdb_id} after {self.max_retries} attempts"
                    )
                    return None

    def fetch_polymer_entities(self, pdb_id: str) -> Optional[List[Dict]]:
        """Fetch polymer entity information for a PDB entry.

        Args:
            pdb_id (str): The PDB ID to fetch polymer entities for.

        Returns:
            Optional[List[Dict]]: List of polymer entity dictionaries, or None if failed.

        Example:
            entities = builder.fetch_polymer_entities("1ABC")
            for entity in entities:
            ...     print(f"Entity {entity.get('entity_id')}: {entity.get('title', 'No title')}")
        """
        if not self.validate_pdb_id(pdb_id):
            logger.error(f"Invalid PDB ID format: {pdb_id}")
            return None

        url = f"{self.rcsb_base_url}/polymer_entity/{pdb_id}"

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                # Handle both single entity and multiple entities
                if isinstance(data, dict):
                    return [data]
                elif isinstance(data, list):
                    return data
                else:
                    logger.error(f"Unexpected response format for {pdb_id}")
                    return None

            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {pdb_id}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to fetch polymer entities for {pdb_id} after {self.max_retries} attempts"
                    )
                    return None

    def fetch_fasta_sequence(self, pdb_id: str, entity_id: str) -> Optional[str]:
        """Fetch FASTA sequence for a specific polymer entity.

        Args:
            pdb_id (str): The PDB ID.
            entity_id (str): The polymer entity ID.

        Returns:
            Optional[str]: FASTA sequence string, or None if failed.

        Example:
            sequence = builder.fetch_fasta_sequence("1ABC", "1")
            if sequence:
            ...     print(sequence[:100])  # First 100 characters
        """
        if not self.validate_pdb_id(pdb_id):
            logger.error(f"Invalid PDB ID format: {pdb_id}")
            return None

        url = f"{self.rcsb_base_url}/polymer_entity/{pdb_id}/{entity_id}"

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                # Extract sequence from response
                sequence = (
                    data.get("entity", {})
                    .get("polymer_seq", {})
                    .get("one_letter_code", "")
                )
                if sequence:
                    return sequence
                else:
                    logger.warning(f"No sequence found for {pdb_id} entity {entity_id}")
                    return None

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed for {pdb_id} entity {entity_id}: {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to fetch sequence for {pdb_id} entity {entity_id} after {self.max_retries} attempts"
                    )
                    return None

    def get_entity_info(self, pdb_id: str, entity_id: str) -> Optional[Dict]:
        """Get detailed information about a specific polymer entity.

        Args:
            pdb_id (str): The PDB ID.
            entity_id (str): The polymer entity ID.

        Returns:
            Optional[Dict]: Dictionary containing entity information, or None if failed.

        Example:
            info = builder.get_entity_info("1ABC", "1")
            print(f"Title: {info.get('title', 'No title')}")
            print(f"Type: {info.get('entity', {}).get('type', 'Unknown')}")
        """
        if not self.validate_pdb_id(pdb_id):
            logger.error(f"Invalid PDB ID format: {pdb_id}")
            return None

        url = f"{self.rcsb_base_url}/polymer_entity/{pdb_id}/{entity_id}"

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed for {pdb_id} entity {entity_id}: {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to fetch entity info for {pdb_id} entity {entity_id} after {self.max_retries} attempts"
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
            success, message = builder.build_fasta_from_pdb("1ABC", "protein.fasta")
            print(message)
        """
        if not self.validate_pdb_id(pdb_id):
            return False, f"Invalid PDB ID format: {pdb_id}"

        # Get polymer entities
        entities = self.fetch_polymer_entities(pdb_id)
        if not entities:
            return False, f"No polymer entities found for PDB ID: {pdb_id}"

        # Generate output filename if not provided
        if output_file is None:
            output_file = f"{pdb_id}_protein.fasta"

        try:
            with open(output_file, "w") as f:
                for entity in entities:
                    entity_id = entity.get("entity_id", "1")

                    # Get entity information
                    entity_info = self.get_entity_info(pdb_id, entity_id)
                    if not entity_info:
                        logger.warning(
                            f"Could not fetch info for {pdb_id} entity {entity_id}"
                        )
                        continue

                    # Get sequence
                    sequence = self.fetch_fasta_sequence(pdb_id, entity_id)
                    if not sequence:
                        logger.warning(
                            f"No sequence found for {pdb_id} entity {entity_id}"
                        )
                        continue

                    # Extract title and other metadata
                    title = entity_info.get("title", f"Unknown protein from {pdb_id}")
                    entity_type = entity_info.get("entity", {}).get("type", "Unknown")

                    # Write FASTA entry
                    f.write(f">pdb|{pdb_id}|entity_{entity_id}|{entity_type}|{title}\n")

                    # Write sequence in 80-character lines
                    for i in range(0, len(sequence), 80):
                        f.write(sequence[i: i + 80] + "\n")
                    f.write("\n")

            return True, f"Successfully created FASTA file: {output_file}"

        except Exception as e:
            logger.error(f"Error writing FASTA file: {e}")
            return False, f"Error writing FASTA file: {e}"

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

                    # Get polymer entities
                    entities = self.fetch_polymer_entities(pdb_id)
                    if not entities:
                        failed_pdbs.append(f"{pdb_id} (no polymer entities)")
                        continue

                    pdb_success = False
                    for entity in entities:
                        entity_id = entity.get("entity_id", "1")

                        # Get entity information
                        entity_info = self.get_entity_info(pdb_id, entity_id)
                        if not entity_info:
                            continue

                        # Get sequence
                        sequence = self.fetch_fasta_sequence(pdb_id, entity_id)
                        if not sequence:
                            continue

                        # Extract title and other metadata
                        title = entity_info.get(
                            "title", f"Unknown protein from {pdb_id}"
                        )
                        entity_type = entity_info.get("entity", {}).get(
                            "type", "Unknown"
                        )

                        # Write FASTA entry
                        f.write(
                            f">pdb|{pdb_id}|entity_{entity_id}|{entity_type}|{title}\n"
                        )

                        # Write sequence in 80-character lines
                        for i in range(0, len(sequence), 80):
                            f.write(sequence[i: i + 80] + "\n")
                        f.write("\n")

                        pdb_success = True

                    if pdb_success:
                        successful_pdbs.append(pdb_id)
                    else:
                        failed_pdbs.append(f"{pdb_id} (no sequences found)")

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

    def list_pdb_entities(self, pdb_id: str) -> Tuple[bool, str]:
        """List all polymer entities in a PDB entry.

        Args:
            pdb_id (str): The PDB ID to list entities for.

        Returns:
            Tuple[bool, str]: (success, message) containing entity information.

        Example:
            success, info = builder.list_pdb_entities("1ABC")
            print(info)
        """
        if not self.validate_pdb_id(pdb_id):
            return False, f"Invalid PDB ID format: {pdb_id}"

        # Get PDB info
        pdb_info = self.fetch_pdb_info(pdb_id)
        if not pdb_info:
            return False, f"Could not fetch PDB info for: {pdb_id}"

        # Get polymer entities
        entities = self.fetch_polymer_entities(pdb_id)
        if not entities:
            return False, f"No polymer entities found for PDB ID: {pdb_id}"

        # Build information string
        title = pdb_info.get("title", "No title available")
        info_lines = [
            f"PDB ID: {pdb_id}",
            f"Title: {title}",
            f"Number of polymer entities: {len(entities)}",
            "",
        ]

        for i, entity in enumerate(entities, 1):
            entity_id = entity.get("entity_id", "1")
            entity_title = entity.get("title", "No title")
            entity_type = entity.get("type", "Unknown")

            info_lines.append(f"Entity {i}:")
            info_lines.append(f"  ID: {entity_id}")
            info_lines.append(f"  Type: {entity_type}")
            info_lines.append(f"  Title: {entity_title}")
            info_lines.append("")

        return True, "\n".join(info_lines)

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
    """Command-line interface for FastaBuilder.

    Usage:
        python build_fasta.py <pdb_id> [output_file]
        python build_fasta.py --multiple <pdb_id1> <pdb_id2> ... [output_file]
        python build_fasta.py --list <pdb_id>
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Build FASTA files from PDB IDs using RCSB PDB database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_fasta.py 1ABC                    # Create 1ABC_protein.fasta
  python build_fasta.py 1ABC my_protein.fasta   # Create custom filename
  python build_fasta.py --multiple 1ABC 2DEF 3GHI combined.fasta
  python build_fasta.py --list 1ABC             # List entities in PDB
  python build_fasta.py --annotate model.cif input.fasta  # Create annotated sequence
        """,
    )

    parser.add_argument("pdb_ids", nargs="*", help="PDB ID(s) to process (not required for --annotate)")

    parser.add_argument(
        "--multiple",
        action="store_true",
        help="Process multiple PDB IDs into a single FASTA file",
    )

    parser.add_argument(
        "--list", action="store_true", help="List polymer entities in PDB entry"
    )

    parser.add_argument(
        "--annotate",
        nargs=2,
        metavar=('CIF_FILE', 'FASTA_FILE'),
        help="Create annotated sequence file from ModelAngelo CIF output and FASTA file"
    )

    parser.add_argument("--output", "-o", help="Output file name (optional)")

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )

    parser.add_argument(
        "--retries", type=int, default=3, help="Maximum retry attempts (default: 3)"
    )

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Create FastaBuilder instance
    builder = FastaBuilder(timeout=args.timeout, max_retries=args.retries)

    if args.annotate:
        # Create annotated sequence from CIF and FASTA files
        cif_file, fasta_file = args.annotate
        output_file = args.output or "annotated_sequence.fasta"

        success, message = builder.create_annotated_sequence(cif_file, fasta_file, output_file)
        print(message)
        sys.exit(0 if success else 1)

    elif args.list:
        # List entities for single PDB ID
        if len(args.pdb_ids) != 1:
            print("Error: --list option requires exactly one PDB ID")
            sys.exit(1)

        success, message = builder.list_pdb_entities(args.pdb_ids[0])
        print(message)
        sys.exit(0 if success else 1)

    elif args.multiple:
        # Process multiple PDB IDs
        output_file = args.output or "combined_protein.fasta"
        success, message = builder.build_fasta_from_multiple_pdbs(
            args.pdb_ids, output_file
        )
        print(message)
        sys.exit(0 if success else 1)

    else:
        # Process single PDB ID
        if not args.pdb_ids:
            print("Error: No PDB ID provided. Use --help for usage information.")
            sys.exit(1)
        elif len(args.pdb_ids) != 1:
            print("Error: Single PDB mode requires exactly one PDB ID")
            sys.exit(1)

        output_file = args.output
        success, message = builder.build_fasta_from_pdb(args.pdb_ids[0], output_file)
        print(message)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
