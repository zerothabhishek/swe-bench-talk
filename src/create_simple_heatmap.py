#!/usr/bin/env python3
"""
Create a simple heatmap visualization from the challenge matrix data.
Candidates are ordered by performance (lowest to highest) on X-axis.
Challenges appear in their original order on Y-axis.
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_and_prepare_data(csv_file):
    """Load the challenge matrix data and prepare it for visualization."""
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Extract the candidate columns (exclude Challenge, Created_At, Difficulty)
    candidate_cols = [col for col in df.columns 
                     if col not in ['Challenge', 'Created_At', 'Difficulty']]
    
    # Sort candidates by total solved challenges (lowest to highest)
    candidate_sums = df[candidate_cols].sum().sort_values()
    candidate_cols_sorted = candidate_sums.index.tolist()
    
    # Reorder the dataframe columns to match the sorted candidate order
    df_sorted = df[['Challenge', 'Created_At', 'Difficulty'] + candidate_cols_sorted]
    
    # Create the matrix for the heatmap
    heatmap_data = df_sorted[candidate_cols_sorted].values
    
    # Get the challenge labels (in original order)
    challenge_labels = df_sorted['Challenge'].values
    
    return heatmap_data, challenge_labels, candidate_cols_sorted, df_sorted

def create_heatmap(heatmap_data, challenge_labels, candidate_cols, df_sorted, output_file):
    """Create and save the heatmap visualization."""
    
    # Set up the plot with extra space at the bottom for statistics
    fig = plt.figure(figsize=(16, 24))
    
    # Create main heatmap subplot (take up most of the space)
    ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=3)
    
    # Create the heatmap
    sns.heatmap(heatmap_data, 
                xticklabels=candidate_cols,
                yticklabels=challenge_labels,  # Show challenge names
                cmap='RdYlGn',  # Red-Yellow-Green colormap
                cbar=False,  # Remove the colorbar/legend
                square=False,
                linewidths=0.5,
                linecolor='white',
                ax=ax1)
    
    # Customize the main heatmap
    ax1.set_title('SWE-Bench Challenge Resolution Heatmap\nChallenges in original order, Candidates ordered by performance', 
                  fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel('Candidates (ordered by performance: lowest to highest)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Challenges (in original order)', fontsize=12, fontweight='bold')
    
    # Rotate x-axis labels for better readability
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    
    # Rotate y-axis labels (challenge names) for better visibility
    ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0, ha='right', fontsize=4)
    
    # Create statistics subplot at the bottom
    ax2 = plt.subplot2grid((4, 1), (3, 0), rowspan=1)
    ax2.axis('off')  # Hide axes for text display
    
    # Calculate statistics
    total_challenges = len(df_sorted)
    total_candidates = len(candidate_cols)
    total_solutions = df_sorted[candidate_cols].sum().sum()
    overall_success_rate = total_solutions/(total_challenges*total_candidates)*100
    
    # Get candidate performance sorted by performance
    candidate_performance = df_sorted[candidate_cols].sum().sort_values(ascending=False)
    
    # Create statistics text
    stats_text = f"""SUMMARY STATISTICS:
Total Challenges: {total_challenges} | Total Candidates: {total_candidates} | Total Solutions: {total_solutions} | Overall Success Rate: {overall_success_rate:.1f}%

CANDIDATE PERFORMANCE (ordered by performance):
"""
    
    # Add candidate performance details
    for i, (candidate, solved) in enumerate(candidate_performance.items()):
        success_rate = solved / total_challenges * 100
        stats_text += f"{i+1:2d}. {candidate}: {solved:3d}/{total_challenges} ({success_rate:5.1f}%)\n"
    
    # Display statistics at the bottom
    ax2.text(0.02, 0.95, stats_text, transform=ax2.transAxes, fontsize=10, 
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight', format='svg')
    print(f"Heatmap saved to {output_file}")
    
    # Close the plot to free memory
    plt.close()

def main():
    # Check command line arguments
    if len(sys.argv) != 3:
        print("Usage: python create_simple_heatmap.py <input_csv> <output_png>")
        print("Example: python create_simple_heatmap.py challenge_matrix_complete.csv heatmap.png")
        return
    
    # Input and output files
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found!")
        return
    
    print(f"Loading challenge matrix data from {input_file}...")
    
    try:
        # Load and prepare the data
        heatmap_data, challenge_labels, candidate_cols, df_sorted = load_and_prepare_data(input_file)
        
        print(f"Data loaded successfully!")
        print(f"Matrix shape: {heatmap_data.shape}")
        print(f"Number of candidates: {len(candidate_cols)}")
        
        # Create summary statistics
        # create_summary_statistics(df_sorted, candidate_cols) # This function is no longer needed
        
        # Create the heatmap
        print(f"\nCreating heatmap visualization...")
        create_heatmap(heatmap_data, challenge_labels, candidate_cols, df_sorted, output_file)
        
        print(f"\nVisualization complete! Heatmap saved as {output_file}")
        
    except Exception as e:
        print(f"Error creating heatmap: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
