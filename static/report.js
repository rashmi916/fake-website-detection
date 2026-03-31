let ctx = document.getElementById("reportChart").getContext("2d");

let chartInstance;

function renderChart(type) {
  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: type,
    data: {
      labels: window.reportData.labels,
      datasets: [{
        label: "Website Checks",
        data: window.reportData.counts,
        backgroundColor: [
          "#28a745",
          "#dc3545",
          "#ffc107",
          "#007bff"
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" }
      }
    }
  });
}

// Default load bar chart
renderChart("bar");

// Functions for buttons
function showChart(type) {
  renderChart(type);
}
