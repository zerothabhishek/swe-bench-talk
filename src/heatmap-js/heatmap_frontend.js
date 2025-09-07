/**
 * Frontend JavaScript for SWE-Bench Interactive Heatmap
 * This file contains the ECharts initialization and interaction logic
 */

// Global variables to store data
let heatmapData = [];
let challenges = [];
let candidates = [];


function copyToClipboard(text) {
  navigator.clipboard.writeText(text);
}

/**
 * Initialize the heatmap with data
 * @param {Array} data - 2D array of heatmap values
 * @param {Array} challengeLabels - Array of challenge names
 * @param {Array} candidateLabels - Array of candidate names
 */
function initializeHeatmap(data, challengeLabels, candidateLabels) {
  heatmapData = data;
  challenges = challengeLabels;
  candidates = candidateLabels;

  // Initialize ECharts
  const chartDom = document.getElementById("heatmap");
  const myChart = echarts.init(chartDom);

  // Transform data for ECharts heatmap format
  const echartsData = [];
  data.forEach((row, rowIndex) => {
    row.forEach((value, colIndex) => {
      echartsData.push([colIndex, rowIndex, value]);
    });
  });

  const option = {
    // title: {
    //     text: 'SWE-Bench Challenge Resolution Heatmap',
    //     left: 'center',
    //     textStyle: {
    //         fontSize: 12,
    //         fontWeight: 'bold'
    //     }
    // },
    tooltip: {
      position: "top",
      formatter: function (params) {
        const candidate = candidates[params.data[0]];
        const challenge = challenges[params.data[1]];
        const value = params.data[2];
        const status = value === 1 ? "Solved" : "Not Solved";
        const color = value === 1 ? "#28a745" : "#dc3545";
        return `
                    <div style="padding: 8px;">
                        <div style="font-weight: bold; margin-bottom: 4px;">${challenge}</div>
                        <div style="margin-bottom: 2px;"><strong>Candidate:</strong> ${candidate}</div>
                        <div style="margin-bottom: 2px;"><strong>Status:</strong> 
                            <span style="color: ${color}; font-weight: bold;">${status}</span>
                        </div>
                    </div>
                `;
      },
    },
    grid: {
      height: "80%",
      top: "1%",
      left: "15%",
      right: "10%",
    },
    xAxis: {
      type: "category",
      data: candidates,
      splitArea: {
        show: true,
      },
      axisLabel: {
        rotate: 45,
        fontSize: 10,
        interval: 0,
      },
      name: "Candidates",
      nameLocation: "middle",
      nameGap: 150,
      nameTextStyle: {
        fontSize: 12,
        fontWeight: "bold",
      },
      boundaryGap: false,
    },
    yAxis: {
      type: "category",
      data: challenges,
      splitArea: {
        show: true,
      },
      axisLabel: {
        fontSize: 8,
        interval: 0,
      },
      name: "Challenges",
      nameLocation: "middle",
      nameGap: 120,
      nameTextStyle: {
        fontSize: 12,
        fontWeight: "bold",
      },
      boundaryGap: false,
    },
    visualMap: {
      min: 0,
      max: 1,
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: "1%",
      inRange: {
        color: ["#dc3545", "#28a745"],
      },
      text: ["Not Solved", "Solved"],
      textStyle: {
        fontSize: 12,
      },
    },
    series: [
      {
        name: "Challenge Resolution",
        type: "heatmap",
        data: echartsData,
        label: {
          show: false,
        },
        itemStyle: {
          // borderColor: 'lightgray',
          // borderWidth: 1,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: "rgba(0, 0, 0, 0.5)",
            borderColor: "white",
            borderWidth: 1,
          },
        },
      },
    ],
  };

  // Set option and render
  myChart.setOption(option);

  // Handle window resize
  window.addEventListener("resize", function () {
    myChart.resize();
  });

  // Add click event for more interactivity
  myChart.on("click", function (params) {
    const candidate = candidates[params.data[0]];
    const challenge = challenges[params.data[1]];
    const value = params.data[2];
    const status = value === 1 ? "Solved" : "Not Solved";

    const [org, repoAndIssue] = challenge.split("__");
    const repoAndIssueParts = repoAndIssue.split("-");
    const repo = repoAndIssueParts.slice(0, -1).join("-"); // all but the last one
    const issue = repoAndIssueParts[repoAndIssueParts.length - 1]; // last one

    const repoUrl = "https://github.com/" + org + "/" + repo + "/pull/" + issue;
    console.log(challenge, repo, issue, repoUrl);

    copyToClipboard(challenge);

    if (window.doNotOpenRepo !== 1) window.open(repoUrl, "_blank");
  });

  return myChart;
}

/**
 * Update the heatmap with new data
 * @param {Array} data - New 2D array of heatmap values
 * @param {Array} challengeLabels - New array of challenge names
 * @param {Array} candidateLabels - New array of candidate names
 */
function updateHeatmap(data, challengeLabels, candidateLabels) {
  heatmapData = data;
  challenges = challengeLabels;
  candidates = candidateLabels;

  // Re-initialize the chart with new data
  const chartDom = document.getElementById("heatmap");
  if (chartDom) {
    echarts.dispose(chartDom);
    initializeHeatmap(data, challengeLabels, candidateLabels);
  }
}

/**
 * Get current heatmap data
 * @returns {Object} Current data object
 */
function getHeatmapData() {
  return {
    data: heatmapData,
    challenges: challenges,
    candidates: candidates,
  };
}

/**
 * Export heatmap as image
 * @param {string} filename - Name of the file to save
 * @param {string} format - Image format ('png' or 'jpeg')
 */
function exportHeatmap(filename = "heatmap", format = "png") {
  const chartDom = document.getElementById("heatmap");
  const myChart = echarts.getInstanceByDom(chartDom);

  if (myChart) {
    const url = myChart.getDataURL({
      type: format,
      pixelRatio: 2,
      backgroundColor: "#fff",
    });

    const link = document.createElement("a");
    link.download = `${filename}.${format}`;
    link.href = url;
    link.click();
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Check if data is available in global variables (set by the main script)
  if (
    typeof window.heatmapData !== "undefined" &&
    typeof window.challengeLabels !== "undefined" &&
    typeof window.candidateLabels !== "undefined"
  ) {
    initializeHeatmap(
      window.heatmapData,
      window.challengeLabels,
      window.candidateLabels
    );
  }
});

// Make functions available globally for external use
window.initializeHeatmap = initializeHeatmap;
window.updateHeatmap = updateHeatmap;
window.getHeatmapData = getHeatmapData;
window.exportHeatmap = exportHeatmap;
