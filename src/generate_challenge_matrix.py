#!/usr/bin/env python3
"""
Extract resolved challenges from SWE-bench result files and generate a matrix CSV
showing which candidates solved which challenges, using data/instances.csv as the
root source of all challenges.
"""

import sys
import json
import csv
import os
from pathlib import Path
from collections import defaultdict

def extract_candidate_name(file_path):
    """Extract candidate name from file path."""
    # Extract the directory name before 'results'
    parts = file_path.parts
    for i, part in enumerate(parts):
        if part == 'results' and i > 0:
            return parts[i-1]
    return "unknown"

def process_results_file(file_path):
    """Process a single results.json file and return resolved challenges."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Extract resolved challenges
        resolved = data.get('resolved', [])
        return resolved
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def load_result_files(result_files_path):
    """Load result file paths from a text file."""
    result_files = []
    try:
        with open(result_files_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    result_files.append(line)
        print(f"Loaded {len(result_files)} result file paths from {result_files_path}")
        return result_files
    except Exception as e:
        print(f"Error loading result files from {result_files_path}: {e}")
        return []

def load_all_challenges(instance_file):
    """Load all challenges from data/instances.csv with their metadata."""
    challenges = {}
    try:
        with open(instance_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                instance_id = row['instance_id']
                created_at = row['created_at']
                difficulty = row['difficulty']
                challenges[instance_id] = {
                    'created_at': created_at,
                    'difficulty': difficulty
                }
        print(f"Loaded {len(challenges)} challenges from data/instances.csv")
        return challenges
    except Exception as e:
        print(f"Error loading challenges from data/instances.csv: {e}")
        return {}

def main():
    # Load result file paths from input file
    if len(sys.argv) != 4:
        print("No result files path provided:")
        print("Usage: python generate_challenge_matrix.py <ResultFile> <InstanceFile> <OutputFile>")
        print("ResultFile: eg. result_files.txt. contains paths of results files")
        print("InstanceFile: eg. data/instances.csv. contains instance data")
        return 1

    result_files_path = sys.argv[1] ## result_files.txt
    instance_file = sys.argv[2] ## data/instances.csv
    output_file = sys.argv[3] ## challenge_matrix_complete.csv

    if not Path(result_files_path).exists():
        print(f"Result file {result_files_path} not found")
        return 1

    if not Path(instance_file).exists():
        print(f"Instance file {instance_file} not found")
        return 1

    result_files = load_result_files(result_files_path)
    
    if not result_files:
        print(f"No result files found in {result_files_path}")
        print("Please create a text file with one result file path per line")
        return
    
    # Load all challenges from instances.csv
    all_challenges = load_all_challenges(instance_file)
    if not all_challenges:
        print("Failed to load challenges, exiting.")
        return
    
    # Dictionary to store challenge -> candidates mapping
    challenge_to_candidates = defaultdict(list)
    # List to store candidate names in order
    candidate_names = []
    
    # Process each result file
    for result_file in result_files:
        file_path = Path(".") / result_file
        
        if not file_path.exists():
            print(f"Warning: {file_path} not found, skipping...")
            continue
        
        candidate_name = extract_candidate_name(file_path)
        candidate_names.append(candidate_name)
        resolved_challenges = process_results_file(file_path)
        
        print(f"Processing {candidate_name}: {len(resolved_challenges)} resolved challenges")
        
        # Add candidate to each resolved challenge
        for challenge in resolved_challenges:
            challenge_to_candidates[challenge].append(candidate_name)
    
    # Generate matrix CSV output with all challenges
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header with challenge metadata and candidate names
        header = ['Challenge', 'Created_At', 'Difficulty'] + candidate_names
        writer.writerow(header)
        
        # Write data rows for ALL challenges (including unsolved ones)
        for challenge_id in sorted(all_challenges.keys()):
            challenge_info = all_challenges[challenge_id]
            row = [
                challenge_id,
                challenge_info['created_at'],
                challenge_info['difficulty']
            ]
            
            # Add candidate columns (1 if solved, 0 if not)
            for candidate in candidate_names:
                if candidate in challenge_to_candidates[challenge_id]:
                    row.append(1)
                else:
                    row.append(0)
            
            writer.writerow(row)
    
    print(f"\nComplete matrix output written to {output_file}")
    print(f"Total challenges: {len(all_challenges)}")
    print(f"Total candidates: {len(candidate_names)}")
    
    # Print some statistics
    total_solutions = sum(len(candidates) for candidates in challenge_to_candidates.values())
    print(f"Total solutions: {total_solutions}")
    
    # Count solved vs unsolved challenges
    solved_challenges = len(challenge_to_candidates)
    unsolved_challenges = len(all_challenges) - solved_challenges
    print(f"Solved challenges: {solved_challenges}")
    print(f"Unsolved challenges: {unsolved_challenges}")
    
    # Show some examples
    print("\nExample challenges:")
    for i, (challenge, candidates) in enumerate(sorted(challenge_to_candidates.items())):
        if i < 5:  # Show first 5
            print(f"  {challenge}: {len(candidates)} candidates")
    
    # Also generate the original format for comparison
    original_output_file = "challenge_solutions.csv"
    
    with open(original_output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Challenge', 'Candidates'])
        
        # Write data rows
        for challenge in sorted(challenge_to_candidates.keys()):
            candidates = challenge_to_candidates[challenge]
            # Join candidates with commas
            candidates_str = ', '.join(candidates)
            writer.writerow([challenge, candidates_str])
    
    print(f"Original format also written to {original_output_file}")

if __name__ == "__main__":
    main()
