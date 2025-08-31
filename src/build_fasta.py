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
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Set up logging
logger = logging.getLogger(__name__)


class FastaBuilder:
    """Build FASTA files from PDB IDs by retrieving sequences from RCSB PDB.

    This class provides methods to fetch FASTA sequences from the RCSB PDB database
    and save them to indexed files for use in cryo-EM software workflows.

    Attributes:
        rcsb_fasta_url (str): Base URL for RCSB PDB FASTA sequences
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

    def fetch_fasta_sequence(self, pdb_id: str) -> Optional[str]:
        """Fetch FASTA sequence for a PDB entry using direct FASTA URL.

        Args:
            pdb_id (str): The PDB ID to fetch FASTA sequence for.

        Returns:
            Optional[str]: FASTA sequence string, or None if failed.

        Example:
            sequence = builder.fetch_fasta_sequence("2BG9")
            if sequence:
                print(sequence[:100])  # First 100 characters
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
                logger.warning(f"Attempt {attempt + 1} failed for {pdb_id}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to fetch FASTA sequence for {pdb_id} after {self.max_retries} attempts"
                    )
                    return None

    def build_fasta_from_pdb(
            self, pdb_id: str, output_file: str
    ) -> Tuple[bool, str]:
        """Build a FASTA file from a single PDB ID.

        Args:
            pdb_id (str): The PDB ID to fetch sequences from.
            output_file (str): Output file path.

        Returns:
            Tuple[bool, str]: (success, message) indicating operation result.

        Example:
            success, message = builder.build_fasta_from_pdb("2BG9", "protein.fasta")
            print(message)
        """
        if not self.validate_pdb_id(pdb_id):
            return False, f"Invalid PDB ID format: {pdb_id}"

        # Fetch FASTA sequence directly from RCSB
        fasta_content = self.fetch_fasta_sequence(pdb_id)
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

                    # Fetch FASTA sequence directly from RCSB
                    fasta_content = self.fetch_fasta_sequence(pdb_id)
                    if fasta_content:
                        # Write FASTA content to file
                        f.write(fasta_content)
                        successful_pdbs.append(pdb_id)
                    else:
                        failed_pdbs.append(pdb_id)

            # Prepare result message
            if successful_pdbs:
                message = f"Successfully created FASTA file: {output_file} with {len(successful_pdbs)} sequences"
                if failed_pdbs:
                    message += f" (Failed: {', '.join(failed_pdbs)})"
                return True, message
            else:
                return False, f"Failed to fetch any sequences. Failed PDB IDs: {', '.join(failed_pdbs)}"

        except Exception as e:
            logger.error(f"Error writing combined FASTA file: {e}")
            return False, f"Error writing combined FASTA file: {e}"

    def create_annotated_sequence(
            self,
            cif_file: str,
            fasta_file: str,
            output_file: str = "structure_sequence_alignment.csv"
    ) -> Tuple[bool, str]:
        """Create a CSV file that aligns CIF structure chains to FASTA sequences with similarity metrics.

        This function takes a protein structure .cif file and a FASTA file, then creates
        a CSV file with three columns: "cif chain", "fasta sequence", "sequence similarity".
        It performs a BLAST-like search to find the best matching FASTA sequence for each
        CIF chain and calculates sequence similarity metrics.

        Args:
            cif_file (str): Path to the protein structure .cif file
            fasta_file (str): Path to the input FASTA file
            output_file (str, optional): Output CSV file name. Defaults to "structure_sequence_alignment.csv".

        Returns:
            Tuple[bool, str]: (success, message) where success is True if the operation
                completed successfully, False otherwise. Message contains details about
                the operation result.

        Example:
            success, message = builder.create_annotated_sequence(
                "protein_structure.cif",
                "sequences.fasta",
                "alignment_results.csv"
            )
        """
        try:
            # Validate input files
            if not os.path.exists(cif_file):
                return False, f"Error: CIF file not found: {cif_file}"

            if not os.path.exists(fasta_file):
                return False, f"Error: FASTA file not found: {fasta_file}"

            # Read and parse the CIF file to extract chain sequences
            cif_chains = self._parse_cif_chains(cif_file)
            if not cif_chains:
                return False, f"Error: Failed to parse CIF file or no chains found: {cif_file}"

            # Read and parse the FASTA file
            fasta_data = self._parse_fasta_file(fasta_file)
            if not fasta_data:
                return False, f"Error: Failed to parse FASTA file: {fasta_file}"

            # Create alignment results
            alignment_results = self._create_chain_alignments(cif_chains, fasta_data)

            # Write the alignment results to CSV file
            self._write_alignment_csv(alignment_results, output_file)

            return True, f"Successfully created alignment CSV file: {output_file} with {len(alignment_results)} chain alignments"

        except Exception as e:
            logger.error(f"Error creating annotated sequence: {str(e)}")
            return False, f"Error: {str(e)}"

    def _parse_cif_chains(self, cif_file: str) -> Optional[Dict[str, str]]:
        """Parse a CIF file and extract chain sequences.

        Args:
            cif_file (str): Path to the CIF file

        Returns:
            Optional[Dict[str, str]]: Dictionary mapping chain IDs to sequences, or None if failed
        """
        try:
            chains = {}

            with open(cif_file, 'r') as f:
                lines = f.readlines()

            # Amino acid three-letter to one-letter code mapping
            aa_mapping = {
                'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
                'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
                'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
                'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
                'SEC': 'U', 'PYL': 'O'  # Selenocysteine and Pyrrolysine
            }

            # Parse atom_site section to extract chain sequences
            in_atom_site = False
            chain_residues = {}  # chain_id -> {res_id -> res_name}

            for line in lines:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Check for atom_site section
                if line.startswith('_atom_site.'):
                    in_atom_site = True
                    continue
                elif line.startswith('_') and not line.startswith('_atom_site.'):
                    in_atom_site = False
                    continue

                if in_atom_site and line and not line.startswith('_'):
                    # Parse atom_site data line
                    parts = line.split()
                    if len(parts) >= 6:  # Should have at least chain_id, res_id, res_name
                        try:
                            # Find chain_id, res_id, and res_name columns
                            # This is a simplified parser - in real CIF files, column order may vary
                            chain_id = parts[0]  # Assuming chain_id is first
                            res_id = parts[1]  # Assuming res_id is second
                            res_name = parts[2]  # Assuming res_name is third

                            # Only process protein residues
                            if res_name in aa_mapping:
                                if chain_id not in chain_residues:
                                    chain_residues[chain_id] = {}
                                chain_residues[chain_id][res_id] = res_name
                        except (IndexError, ValueError):
                            continue

            # Convert chain_residues to sequences
            for chain_id, residues in chain_residues.items():
                # Sort residues by residue ID (convert to int for proper sorting)
                sorted_residues = sorted(residues.items(), key=lambda x: int(x[0]) if x[0].isdigit() else float('inf'))

                sequence = []
                for res_id, res_name in sorted_residues:
                    sequence.append(aa_mapping[res_name])

                if sequence:  # Only add chains with valid sequences
                    chains[chain_id] = ''.join(sequence)

            return chains if chains else None

        except Exception as e:
            logger.error(f"Error parsing CIF chains: {str(e)}")
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

    def _create_chain_alignments(self, cif_chains: Dict[str, str], fasta_data: Dict[str, str]) -> List[Dict]:
        """Create alignments between CIF chains and FASTA sequences with similarity metrics.

        Args:
            cif_chains (Dict[str, str]): Dictionary mapping chain IDs to sequences
            fasta_data (Dict[str, str]): Dictionary mapping FASTA headers to sequences

        Returns:
            List[Dict]: List of alignment results with chain, sequence, and similarity info
        """
        alignment_results = []

        for chain_id, chain_sequence in cif_chains.items():
            best_match = None
            best_similarity = 0.0

            # Find the best matching FASTA sequence for this chain
            for fasta_header, fasta_sequence in fasta_data.items():
                similarity = self._calculate_sequence_similarity(chain_sequence, fasta_sequence)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = fasta_header

            # Add result to alignment_results
            alignment_results.append({
                'cif_chain': chain_id,
                'fasta_sequence': best_match if best_match else "No match found",
                'sequence_similarity': f"{best_similarity:.4f}" if best_match else "0.0000"
            })

        return alignment_results

    def _calculate_sequence_similarity(self, seq1: str, seq2: str) -> float:
        """Calculate sequence similarity between two sequences using local alignment.

        Args:
            seq1 (str): First sequence
            seq2 (str): Second sequence

        Returns:
            float: Similarity score between 0.0 and 1.0
        """
        if not seq1 or not seq2:
            return 0.0

        # Use a simple local alignment algorithm (similar to BLAST)
        # This is a simplified version - for production use, consider using BioPython's BLAST

        # Find the longest common substring as a proxy for local alignment
        def longest_common_substring(s1, s2):
            m = [[0] * (1 + len(s2)) for _ in range(1 + len(s1))]
            longest = 0
            for x in range(len(s1)):
                for y in range(len(s2)):
                    if s1[x] == s2[y]:
                        m[x + 1][y + 1] = m[x][y] + 1
                        longest = max(longest, m[x + 1][y + 1])
            return longest

        # Calculate similarity using multiple metrics
        lcs_length = longest_common_substring(seq1, seq2)

        # Calculate identity (exact matches)
        min_len = min(len(seq1), len(seq2))
        if min_len == 0:
            return 0.0

        # Count exact matches
        exact_matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
        identity = exact_matches / min_len

        # Calculate coverage (how much of the shorter sequence is covered by the longer one)
        coverage = lcs_length / min_len

        # Combine metrics (weighted average)
        similarity = (0.6 * identity + 0.4 * coverage)

        return min(similarity, 1.0)  # Ensure it doesn't exceed 1.0

    def _write_alignment_csv(self, alignment_results: List[Dict], output_file: str):
        """Write alignment results to CSV file.

        Args:
            alignment_results (List[Dict]): List of alignment results
            output_file (str): Output CSV file path
        """
        import csv

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(['cif_chain', 'fasta_sequence', 'sequence_similarity'])

            # Write data rows
            for result in alignment_results:
                writer.writerow([
                    result['cif_chain'],
                    result['fasta_sequence'],
                    result['sequence_similarity']
                ])


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
            args.pdb_ids, args.output or "combined_protein.fasta"
        )
    else:
        success, message = builder.build_fasta_from_pdb(
            args.pdb_ids[0], args.output
        )

    print(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
