#!/usr/bin/env python3
"""
Create difficulty-specific heatmap visualizations from the challenge matrix data.
Generates separate heatmaps for each difficulty level to provide cleaner visualizations
with fewer data points on the Y-axis.
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import os

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
    
    return df_sorted, candidate_cols_sorted

def create_difficulty_heatmap(df_filtered, candidate_cols, difficulty_level, output_dir):
    """Create a heatmap for a specific difficulty level."""
    
    if len(df_filtered) == 0:
        print(f"No challenges found for difficulty level: {difficulty_level}")
        return
    
    # Create the matrix for the heatmap
    heatmap_data = df_filtered[candidate_cols].values
    
    # Get the challenge labels
    challenge_labels = df_filtered['Challenge'].values
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(16, max(8, len(challenge_labels) * 0.3)))
    
    # Create the heatmap
    sns.heatmap(heatmap_data, 
                xticklabels=candidate_cols,
                yticklabels=challenge_labels,
                cmap='RdYlGn',  # Red-Yellow-Green colormap
                cbar_kws={'label': 'Solved (1) / Not Solved (0)'},
                square=False,
                linewidths=0.5,
                linecolor='white',
                ax=ax)
    
    # Customize the heatmap
    ax.set_title(f'SWE-Bench Challenge Resolution Heatmap\nDifficulty Level: {difficulty_level}\n({len(challenge_labels)} challenges)', 
                  fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Candidates (ordered by performance: lowest to highest)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Challenges (ordered by creation date)', fontsize=12, fontweight='bold')
    
    # Rotate x-axis labels for better readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    
    # Rotate y-axis labels for better readability if there are many challenges
    if len(challenge_labels) > 20:
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)
    else:
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=10)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Create filename for this difficulty level
    difficulty_filename = difficulty_level.replace(' ', '_').replace('-', '_').replace('>', 'gt_').replace('<', 'lt_')
    output_file = os.path.join(output_dir, f'heatmap_{difficulty_filename}.png')
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Heatmap for '{difficulty_level}' saved to {output_file}")
    
    # Close the plot to free memory
    plt.close()
    
    return output_file

def create_combined_difficulty_heatmap(df_sorted, candidate_cols, output_dir):
    """Create a combined heatmap showing all difficulty levels together."""
    
    # Create the matrix for the heatmap
    heatmap_data = df_sorted[candidate_cols].values
    
    # Get the challenge labels and difficulty labels
    challenge_labels = df_sorted['Challenge'].values
    difficulty_labels = df_sorted['Difficulty'].values
    
    # Set up the plot with extra space on the left for labels
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, max(12, len(challenge_labels) * 0.2)), 
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
    ax2.set_title('SWE-Bench Challenge Resolution Heatmap\nAll Difficulty Levels Combined\nChallenges ordered by difficulty level (hardest at top)', 
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
    output_file = os.path.join(output_dir, 'heatmap_all_difficulties_combined.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Combined difficulty heatmap saved to {output_file}")
    
    # Close the plot to free memory
    plt.close()
    
    return output_file

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

def create_difficulty_specific_statistics(df_sorted, candidate_cols):
    """Create and display difficulty-specific statistics."""
    print("\n=== DIFFICULTY-SPECIFIC STATISTICS ===")
    
    difficulty_levels = ['> 4 hours', '1-4 hours', '15 min - 1 hour', '<15 min fix']
    
    for difficulty in difficulty_levels:
        df_filtered = df_sorted[df_sorted['Difficulty'] == difficulty]
        
        if len(df_filtered) > 0:
            print(f"\n--- {difficulty} ---")
            print(f"Number of challenges: {len(df_filtered)}")
            
            # Calculate success rates for this difficulty level
            difficulty_solutions = df_filtered[candidate_cols].sum().sum()
            total_possible = len(df_filtered) * len(candidate_cols)
            success_rate = difficulty_solutions / total_possible * 100
            
            print(f"Total solutions: {difficulty_solutions}/{total_possible}")
            print(f"Success rate: {success_rate:.1f}%")
            
            # Top performers for this difficulty level
            candidate_performance = df_filtered[candidate_cols].sum().sort_values(ascending=False)
            print("Top 3 performers:")
            for i, (candidate, solved) in enumerate(candidate_performance.head(3).items()):
                success_rate = solved / len(df_filtered) * 100
                print(f"  {i+1}. {candidate}: {solved}/{len(df_filtered)} ({success_rate:.1f}%)")

def main():
    # Input and output files
    if len(sys.argv) < 2:
        print("Usage: python create_difficulty_heatmaps.py <input_csv_file> [output_directory]")
        print("Example: python create_difficulty_heatmaps.py challenge_matrix.csv heatmaps/")
        return
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "heatmaps"
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found!")
        print("Please run extract_results.py first to generate the challenge matrix.")
        return
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("Loading challenge matrix data...")
    
    try:
        # Load and prepare the data
        df_sorted, candidate_cols = load_and_prepare_data(input_file)
        
        print(f"Data loaded successfully!")
        print(f"Matrix shape: {df_sorted[candidate_cols].shape}")
        print(f"Number of candidates: {len(candidate_cols)}")
        
        # Create summary statistics
        create_summary_statistics(df_sorted, candidate_cols)
        create_difficulty_specific_statistics(df_sorted, candidate_cols)
        
        # Define difficulty levels
        difficulty_levels = ['> 4 hours', '1-4 hours', '15 min - 1 hour', '<15 min fix']
        
        # Create individual heatmaps for each difficulty level
        print("\nCreating difficulty-specific heatmaps...")
        created_files = []
        
        for difficulty in difficulty_levels:
            print(f"\nProcessing difficulty level: {difficulty}")
            df_filtered = df_sorted[df_sorted['Difficulty'] == difficulty]
            
            if len(df_filtered) > 0:
                output_file = create_difficulty_heatmap(df_filtered, candidate_cols, difficulty, output_dir)
                if output_file:
                    created_files.append(output_file)
            else:
                print(f"No challenges found for difficulty level: {difficulty}")
        
        # Create combined heatmap
        print("\nCreating combined difficulty heatmap...")
        combined_file = create_combined_difficulty_heatmap(df_sorted, candidate_cols, output_dir)
        if combined_file:
            created_files.append(combined_file)
        
        print(f"\nVisualization complete! Created {len(created_files)} heatmap files:")
        for file_path in created_files:
            print(f"  - {file_path}")
        
        print(f"\nAll heatmaps saved in directory: {output_dir}")
        
    except Exception as e:
        print(f"Error creating heatmaps: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
