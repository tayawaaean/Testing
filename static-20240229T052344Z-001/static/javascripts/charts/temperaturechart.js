document.addEventListener('DOMContentLoaded', function () {
    // Initialize Chart.js for Temperature
    var ctxTemperature = document.getElementById('temperatureChart').getContext('2d');

    ctxTemperature.canvas.width = 600; 
    ctxTemperature.canvas.height = 297;

    var temperatureData = {
        labels: [],
        datasets: [{
            label: 'Temperature',
            borderColor: 'red',
            data: [],
            fill: false,
        }]
    };

    var temperatureChart = new Chart(ctxTemperature, {
        type: 'line',
        data: temperatureData,
        options: {
            scales: {
                x: [{
                    display: false, // Hide x-axis labels
                    type: 'linear',
                    position: 'bottom'
                }]
            }
        }
    });

    // Initialize flatpickr for the date input for Temperature
    flatpickr("#temperature-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        defaultDate: "today", // Set the default date to today
    });

    // Function to update chart with data from the server for Temperature
    function updateTemperatureChart() {
        // Get the selected date from the input for Temperature
        var selectedDate = document.getElementById('temperature-date-input').value;

        // Make an AJAX request to fetch temperature data for the selected date from the server
        fetch('/get_temperature_data_for_date/' + selectedDate)
            .then(response => response.json())
            .then(data => {
                // Clear existing data for Temperature
                temperatureData.labels = [];
                temperatureData.datasets[0].data = [];

                // Add new data points
                data.forEach(entry => {
                    temperatureData.labels.push(entry.time);
                    temperatureData.datasets[0].data.push(entry.temperature);
                });

                // Update the chart for Temperature
                temperatureChart.update();
            })
            .catch(error => console.error('Error fetching temperature data:', error));
    }

    // You can also handle the 'Enter' key press to trigger the function for Temperature
    var temperatureDateInput = flatpickr("#temperature-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        onChange: function (selectedDates, dateStr, instance) {
            // Call the updateTemperatureChart function when the date is selected for Temperature
            updateTemperatureChart();
        }
    });

    // Initial update when the page loads for Temperature
    updateTemperatureChart();
});
