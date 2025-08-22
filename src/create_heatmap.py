#!/usr/bin/env python3
"""
Create a heatmap visualization from the challenge matrix data.
Challenges are ordered by difficulty level on Y-axis, candidates on X-axis.
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def load_and_prepare_data(csv_file):
    """Load the challenge matrix data and prepare it for visualization."""
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Define difficulty order for sorting (hardest first, easiest last)
    difficulty_order = ['> 4 hours', '1-4 hours', '15 min - 1 hour', '<15 min fix']
    
    # Create a difficulty mapping for sorting
    difficulty_mapping = {diff: idx for idx, diff in enumerate(difficulty_order)}
    
    # Add a numeric difficulty column for sorting
    df['difficulty_numeric'] = df['Difficulty'].map(difficulty_mapping)
    
    # Sort by difficulty first (hardest first), then by creation date within each difficulty
    df_sorted = df.sort_values(['difficulty_numeric', 'Created_At'])
    
    # Extract the candidate columns (exclude Challenge, Created_At, Difficulty, difficulty_numeric)
    candidate_cols = [col for col in df_sorted.columns 
                     if col not in ['Challenge', 'Created_At', 'Difficulty', 'difficulty_numeric']]
    
    # Sort candidates by total solved challenges (lowest to highest)
    candidate_sums = df_sorted[candidate_cols].sum().sort_values()
    candidate_cols_sorted = candidate_sums.index.tolist()
    
    # Reorder the dataframe columns to match the sorted candidate order
    df_sorted = df_sorted[['Challenge', 'Created_At', 'Difficulty', 'difficulty_numeric'] + candidate_cols_sorted]
    
    # Create the matrix for the heatmap
    heatmap_data = df_sorted[candidate_cols_sorted].values
    
    # Get the sorted challenge labels and difficulty labels
    challenge_labels = df_sorted['Challenge'].values
    difficulty_labels = df_sorted['Difficulty'].values
    
    return heatmap_data, challenge_labels, difficulty_labels, candidate_cols_sorted, df_sorted

def create_heatmap(heatmap_data, challenge_labels, difficulty_labels, candidate_cols, output_file):
    """Create and save the heatmap visualization."""
    
    # Set up the plot with extra space on the left for labels
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 20), 
                                   gridspec_kw={'width_ratios': [1, 4]})
    
    # Create the main heatmap on the right subplot
    sns.heatmap(heatmap_data, 
                xticklabels=candidate_cols,
                yticklabels=False,  # Don't show individual challenge labels (too many)
                cmap='RdYlGn',  # Red-Yellow-Green colormap
                cbar_kws={'label': 'Solved (1) / Not Solved (0)'},
                square=False,
                linewidths=0.5,
                linecolor='white',
                ax=ax2)
    
    # Add difficulty level separators and labels on the main heatmap
    current_difficulty = None
    y_positions = []
    difficulty_positions = []
    
    for i, difficulty in enumerate(difficulty_labels):
        if difficulty != current_difficulty:
            if current_difficulty is not None:
                # Draw a line to separate difficulty levels
                ax2.axhline(y=i, color='black', linewidth=2)
            current_difficulty = difficulty
            y_positions.append(i)
            difficulty_positions.append(difficulty)
    
    # Add a final line at the bottom
    ax2.axhline(y=len(difficulty_labels), color='black', linewidth=2)
    
    # Customize the main heatmap
    ax2.set_title('SWE-Bench Challenge Resolution Heatmap\nChallenges ordered by difficulty level (hardest at top)', 
                  fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlabel('Candidates (ordered by performance: lowest to highest)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Challenges (ordered by difficulty)', fontsize=12, fontweight='bold')
    
    # Rotate x-axis labels for better readability
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Create the left subplot for difficulty labels
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, len(difficulty_labels))
    ax1.set_aspect('equal')
    
    # Add difficulty level labels on the left
    for i, (y_pos, difficulty) in enumerate(zip(y_positions, difficulty_positions)):
        ax1.text(0.5, y_pos + 0.5, difficulty, ha='center', va='center', 
                fontsize=12, fontweight='bold', rotation=0)
    
    # Add the final difficulty label
    if difficulty_positions:
        ax1.text(0.5, len(difficulty_labels) - 0.5, difficulty_positions[-1], 
                ha='center', va='center', fontsize=12, fontweight='bold', rotation=0)
    
    # Customize the left subplot
    ax1.set_title('Difficulty Levels', fontsize=14, fontweight='bold', pad=20)
    ax1.axis('off')  # Hide axes
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Heatmap saved to {output_file}")
    
    # Close the plot to free memory
    plt.close()

def create_summary_statistics(df_sorted, candidate_cols):
    """Create and display summary statistics."""
    print("\n=== SUMMARY STATISTICS ===")
    
    # Overall statistics
    total_challenges = len(df_sorted)
    total_candidates = len(candidate_cols)
    total_solutions = df_sorted[candidate_cols].sum().sum()
    
    print(f"Total challenges: {total_challenges}")
    print(f"Total candidates: {total_candidates}")
    print(f"Total solutions: {total_solutions}")
    print(f"Overall success rate: {total_solutions/(total_challenges*total_candidates)*100:.1f}%")
    
    # Difficulty level statistics
    print("\n=== DIFFICULTY LEVEL BREAKDOWN ===")
    difficulty_stats = df_sorted.groupby('Difficulty').agg({
        'Challenge': 'count'
    }).rename(columns={'Challenge': 'Count'})
    
    for difficulty in ['<15 min fix', '15 min - 1 hour', '1-4 hours', '> 4 hours']:
        if difficulty in difficulty_stats.index:
            count = difficulty_stats.loc[difficulty, 'Count']
            print(f"{difficulty}: {count} challenges")
    
    # Candidate performance statistics
    print("\n=== CANDIDATE PERFORMANCE ===")
    candidate_performance = df_sorted[candidate_cols].sum().sort_values(ascending=False)
    
    for candidate, solved in candidate_performance.items():
        success_rate = solved / total_challenges * 100
        print(f"{candidate}: {solved}/{total_challenges} ({success_rate:.1f}%)")

def main():
    # Input and output files
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found!")
        print("Please run extract_results.py first to generate the challenge matrix.")
        return
    
    print("Loading challenge matrix data...")
    
    try:
        # Load and prepare the data
        heatmap_data, challenge_labels, difficulty_labels, candidate_cols, df_sorted = load_and_prepare_data(input_file)
        
        print(f"Data loaded successfully!")
        print(f"Matrix shape: {heatmap_data.shape}")
        print(f"Number of candidates: {len(candidate_cols)}")
        
        # Create summary statistics
        create_summary_statistics(df_sorted, candidate_cols)
        
        # Create the heatmap
        print("\nCreating heatmap visualization...")
        create_heatmap(heatmap_data, challenge_labels, difficulty_labels, candidate_cols, output_file)
        
        print(f"\nVisualization complete! Heatmap saved as {output_file}")
        
    except Exception as e:
        print(f"Error creating heatmap: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
