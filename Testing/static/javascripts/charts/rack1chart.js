document.addEventListener('DOMContentLoaded', function () {
    // Initialize Chart.js for Light Level (lumens1)
    var ctxLumens1 = document.getElementById('lightLevelChart').getContext('2d');
    var lumens1Data = {
        labels: [],
        datasets: [{
            label: 'Light Level',
            borderColor: 'lightgreen',
            data: [],
            fill: false,
        }]
    };

    var lumens1Chart = new Chart(ctxLumens1, {
        type: 'line',
        data: lumens1Data,
        options: {
            scales: {
                x: [{
                    type: 'linear',
                    position: 'bottom'
                }]
            }
        }
    });

    // Initialize flatpickr for the date input for Light Level (lumens1)
    flatpickr("#lumens1-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        defaultDate: "today", // Set the default date to today
    });

    // Function to update chart with data from the server for Light Level (lumens1)
    function updateLumens1Chart() {
        // Get the selected date from the input for Light Level (lumens1)
        var selectedDate = document.getElementById('lumens1-date-input').value;

        // Make an AJAX request to fetch lumens1 data for the selected date from the server
        fetch('/get_lumens1_data_for_date/' + selectedDate)
            .then(response => response.json())
            .then(data => {
                // Clear existing data for Light Level (lumens1)
                lumens1Data.labels = [];
                lumens1Data.datasets[0].data = [];

                // Populate chart data with fetched data
                data.forEach(entry => {
                    lumens1Data.labels.push(entry.time); // Use time as x-axis label
                    lumens1Data.datasets[0].data.push(entry.lumens1);
                });

                // Update the chart for Light Level (lumens1)
                lumens1Chart.update();
            })
            .catch(error => console.error('Error fetching lumens1 data:', error));
    }

    // You can also handle the 'Enter' key press to trigger the function for Light Level (lumens1)
    var lumens1DateInput = flatpickr("#lumens1-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        onChange: function (selectedDates, dateStr, instance) {
            // Call the updateLumens1Chart function when the date is selected for Light Level (lumens1)
            updateLumens1Chart();
        }
    });

    // Initial update when the page loads for Light Level (lumens1)
    updateLumens1Chart();
});
