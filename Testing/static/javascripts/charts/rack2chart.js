document.addEventListener('DOMContentLoaded', function () {
    // Initialize Chart.js for Lumens2
    var ctxLumens2 = document.getElementById('lightChart').getContext('2d');
    var lumens2Data = {
        labels: [],
        datasets: [{
            label: 'Lumens2 Intensity',
            borderColor: 'black',
            data: [],
            fill: false,
        }]
    };

    var lumens2Chart = new Chart(ctxLumens2, {
        type: 'line',
        data: lumens2Data,
        options: {
            scales: {
                x: [{
                    type: 'linear',
                    position: 'bottom'
                }]
            }
        }
    });

    // Initialize flatpickr for Lumens2 date input
    flatpickr("#lumens2-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        defaultDate: "today", // Set the default date to today
    });

    // Function to update chart with data from the server for Lumens2
    function updateLumens2Chart() {
        // Get the selected date from the input for Lumens2
        var selectedDate = document.getElementById('lumens2-date-input').value;

        // Make an AJAX request to fetch Lumens2 data for the selected date from the server
        fetch('/get_lumens2_data_for_date/' + selectedDate)
            .then(response => response.json())
            .then(data => {
                // Clear existing data for Lumens2
                lumens2Data.labels = [];
                lumens2Data.datasets[0].data = [];

                // Populate chart data with fetched data
                data.forEach(entry => {
                    lumens2Data.labels.push(entry.time); // Use time as x-axis label
                    lumens2Data.datasets[0].data.push(entry.lumens2);
                });

                // Update the chart for Lumens2
                lumens2Chart.update();
            })
            .catch(error => console.error('Error fetching Lumens2 data:', error));
    }

    // You can also handle the 'Enter' key press to trigger the function for Lumens2
    var lumens2DateInput = flatpickr("#lumens2-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        onChange: function (selectedDates, dateStr, instance) {
            // Call the updateLumens2Chart function when the date is selected for Lumens2
            updateLumens2Chart();
        }
    });

    // Initial update when the page loads for Lumens2
    updateLumens2Chart();
});
