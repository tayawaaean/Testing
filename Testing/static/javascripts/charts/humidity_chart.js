document.addEventListener('DOMContentLoaded', function () {
    // Initialize Chart.js for Humidity
    var ctxHumidity = document.getElementById('humidityChart').getContext('2d');

    var humidityData = {
        labels: [],
        datasets: [{
            label: 'Humidity',
            borderColor: 'rgb(75, 192, 192)',
            data: [],
            fill: false,
        }]
    };

    var humidityChart = new Chart(ctxHumidity, {
        type: 'line',
        data: humidityData,
        options: {
            scales: {
                x: [{
                    type: 'linear',
                    position: 'bottom',
                    display: 'false'
                }]
            }
        }
    });

    // Initialize flatpickr for the date input for Humidity
    flatpickr("#humidity-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        defaultDate: "today", // Set the default date to today
    });

    // Function to update chart with data from the server for Humidity
    function updateHumidityChart() {
        // Get the selected date from the input for Humidity
        var selectedDate = document.getElementById('humidity-date-input').value;

        // Make an AJAX request to fetch humidity data for the selected date from the server
        fetch('/get_humidity_data_for_date/' + selectedDate)
            .then(response => response.json())
            .then(data => {
                // Clear existing data for Humidity
                humidityData.labels = [];
                humidityData.datasets[0].data = [];

                // Populate chart data with fetched data
                data.forEach(entry => {
                    humidityData.labels.push(entry.time); // Use time as x-axis label
                    humidityData.datasets[0].data.push(entry.humidity);
                });

                // Update the chart for Humidity
                humidityChart.update();
            })
            .catch(error => console.error('Error fetching humidity data:', error));
    }

    // You can also handle the 'Enter' key press to trigger the function for Humidity
    var humidityDateInput = flatpickr("#humidity-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        onChange: function (selectedDates, dateStr, instance) {
            // Call the updateHumidityChart function when the date is selected for Humidity
            updateHumidityChart();
        }
    });

    // Initial update when the page loads for Humidity
    updateHumidityChart();
});
