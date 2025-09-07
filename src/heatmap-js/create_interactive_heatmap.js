#!/usr/bin/env node
/**
 * Create an interactive heatmap visualization from the challenge matrix data using Apache ECharts.
 * Candidates are ordered by performance (lowest to highest) on X-axis.
 * Challenges appear in their original order on Y-axis.
 * 
 * Usage: node create_interactive_heatmap.js <input_csv> <output_html>
 * Example: node create_interactive_heatmap.js challenge_matrix_complete.csv heatmap.html
 */

const fs = require('fs');
const path = require('path');

function parseCSV(csvContent) {
    const lines = csvContent.trim().split('\n');
    const headers = lines[0].split(',');

    // Extract candidate columns (exclude Challenge, Created_At, Difficulty)
    const candidateCols = headers.filter(col =>
        !['Challenge', 'Created_At', 'Difficulty'].includes(col)
    );

    const data = [];
    const challengeLabels = [];

    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        const challenge = values[0];
        challengeLabels.push(challenge);

        const row = [];
        for (let j = 3; j < values.length; j++) { // Skip Challenge, Created_At, Difficulty
            row.push(parseInt(values[j]) || 0);
        }
        data.push(row);
    }

    return { data, challengeLabels, candidateCols };
}

function sortCandidatesByPerformance(data, candidateCols) {
    // Calculate total solved challenges for each candidate
    const candidateSums = {};
    candidateCols.forEach((candidate, index) => {
        candidateSums[candidate] = data.reduce((sum, row) => sum + row[index], 0);
    });

    // Sort candidates by performance (lowest to highest)
    const sortedCandidates = Object.entries(candidateSums)
        .sort(([, a], [, b]) => a - b)
        .map(([candidate]) => candidate);

    // Reorder data matrix to match sorted candidates
    const sortedData = data.map(row => {
        return sortedCandidates.map(candidate => {
            const originalIndex = candidateCols.indexOf(candidate);
            return row[originalIndex];
        });
    });

    return { sortedData, sortedCandidates, candidateSums };
}

function generateHTML(heatmapData, challengeLabels, candidateCols, candidateSums, totalChallenges, totalCandidates, totalSolutions) {
    const overallSuccessRate = (totalSolutions / (totalChallenges * totalCandidates) * 100).toFixed(1);

    // Create candidate performance summary
    const candidatePerformance = Object.entries(candidateSums)
        .sort(([, a], [, b]) => b - a)
        .map(([candidate, solved], index) => {
            const successRate = (solved / totalChallenges * 100).toFixed(1);
            return `${(index + 1).toString().padStart(2)}. ${candidate.padEnd(45)} ${solved.toString().padStart(3)}/${totalChallenges} ${successRate.padStart(5)}%`;
        })
        .join('\n');

    // Read the HTML template
    const templatePath = path.join(__dirname, 'heatmap_template.html');
    let htmlTemplate = fs.readFileSync(templatePath, 'utf8');

    // Replace template placeholders with actual data
    htmlTemplate = htmlTemplate
        .replace('{{TOTAL_CHALLENGES}}', totalChallenges)
        .replace('{{TOTAL_CANDIDATES}}', totalCandidates)
        .replace('{{TOTAL_SOLUTIONS}}', totalSolutions)
        .replace('{{OVERALL_SUCCESS_RATE}}', overallSuccessRate)
        .replace('{{CANDIDATE_PERFORMANCE}}', candidatePerformance);

    // Add data initialization script
    const dataScript = `
    <script>
        // Initialize data for the frontend
        window.heatmapData = ${JSON.stringify(heatmapData)};
        window.challengeLabels = ${JSON.stringify(challengeLabels)};
        window.candidateLabels = ${JSON.stringify(candidateCols)};
    </script>`;

    // Insert the data script before the frontend script
    // htmlTemplate = htmlTemplate.replace('<script src="heatmap_frontend.js"></script>', dataScript + '\n    <script src="heatmap_frontend.js"></script>');
    htmlTemplate = htmlTemplate.replace('<datascript />', dataScript);

    return htmlTemplate;
}

function main() {
    const args = process.argv.slice(2);

    if (args.length !== 2) {
        console.log("Usage: node create_interactive_heatmap.js <input_csv> <output_html>");
        console.log("Example: node create_interactive_heatmap.js challenge_matrix_complete.csv heatmap.html");
        process.exit(1);
    }

    const inputFile = args[0];
    const outputFile = args[1];

    // Check if input file exists
    if (!fs.existsSync(inputFile)) {
        console.error(`Error: ${inputFile} not found!`);
        process.exit(1);
    }

    console.log(`Loading challenge matrix data from ${inputFile}...`);

    try {
        // Read and parse CSV file
        const csvContent = fs.readFileSync(inputFile, 'utf8');
        const { data, challengeLabels, candidateCols } = parseCSV(csvContent);

        console.log("Data loaded successfully!");
        console.log(`Matrix shape: ${data.length} x ${candidateCols.length}`);
        console.log(`Number of candidates: ${candidateCols.length}`);

        // Sort candidates by performance
        const { sortedData, sortedCandidates, candidateSums } = sortCandidatesByPerformance(data, candidateCols);

        // Calculate statistics
        const totalChallenges = data.length;
        const totalCandidates = candidateCols.length;
        const totalSolutions = Object.values(candidateSums).reduce((sum, val) => sum + val, 0);

        console.log(`Total challenges: ${totalChallenges}`);
        console.log(`Total solutions: ${totalSolutions}`);
        console.log(`Overall success rate: ${(totalSolutions / (totalChallenges * totalCandidates) * 100).toFixed(1)}%`);

        // Generate HTML
        console.log("Generating interactive heatmap...");
        const htmlContent = generateHTML(sortedData, challengeLabels, sortedCandidates, candidateSums, totalChallenges, totalCandidates, totalSolutions);

        // Write HTML file
        fs.writeFileSync(outputFile, htmlContent);

        // Copy the frontend JavaScript file to the same directory as the output HTML
        const outputDir = path.dirname(outputFile);
        const frontendSource = path.join(__dirname, 'heatmap_frontend.js');
        const frontendDest = path.join(outputDir, 'heatmap_frontend.js');

        if (fs.existsSync(frontendSource)) {
            fs.copyFileSync(frontendSource, frontendDest);
            console.log(`Frontend JavaScript copied to ${frontendDest}`);
        }

        console.log(`Interactive heatmap saved to ${outputFile}`);
        console.log(`Open ${outputFile} in your web browser to view the interactive heatmap.`);

    } catch (error) {
        console.error(`Error creating interactive heatmap: ${error.message}`);
        console.error(error.stack);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { parseCSV, sortCandidatesByPerformance, generateHTML };
