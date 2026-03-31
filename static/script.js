document.addEventListener("DOMContentLoaded", function () {
  const ctx = document.getElementById("reportChart");

  if (ctx && window.reportData) {
    new Chart(ctx, {
      type: "pie",
      data: {
        labels: window.reportData.labels,
        datasets: [
          {
            data: window.reportData.counts,
            backgroundColor: ["#28a745", "#dc3545"],
          },
        ],
      },
    });
  } else {
    console.error("❌ No report data found!");
  }
});
