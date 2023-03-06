// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example
var ctx2 = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx2, {
  type: 'doughnut',
  data: {
    labels: co_labels,
    datasets: [{
      data: chart_company,
      //backgroundColor: ['#4e73df', '#1cc88a'],
      //borderColor: '#22252B',
      hoverBackgroundColor: '#1cc88a',
      //hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend:false,
    cutoutPercentage: 80,
  },
});
