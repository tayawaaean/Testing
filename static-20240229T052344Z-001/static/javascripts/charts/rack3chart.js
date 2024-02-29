document.addEventListener('DOMContentLoaded', function () {
    // Initialize Chart.js for Lumens3
    var ctxLumens3 = document.getElementById('light1Chart').getContext('2d');
    var lumens3Data = {
        labels: [],
        datasets: [{
            label: 'Lumens3 Intensity',
            borderColor: 'black',
            data: [],
            fill: false,
        }]
    };

    var lumens3Chart = new Chart(ctxLumens3, {
        type: 'line',
        data: lumens3Data,
        options: {
            scales: {
                x: [{
                    type: 'linear',
                    position: 'bottom'
                }]
            }
        }
    });

    // Initialize flatpickr for Lumens3 date input
    flatpickr("#lumens3-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        defaultDate: "today", // Set the default date to today
    });

    // Function to update chart with data from the server for Lumens3
    function updateLumens3Chart() {
        // Get the selected date from the input for Lumens3
        var selectedDate = document.getElementById('lumens3-date-input').value;

        // Make an AJAX request to fetch Lumens3 data for the selected date from the server
        fetch('/get_lumens3_data_for_date/' + selectedDate)
            .then(response => response.json())
            .then(data => {
                // Clear existing data for Lumens3
                lumens3Data.labels = [];
                lumens3Data.datasets[0].data = [];

                // Populate chart data with fetched data
                data.forEach(entry => {
                    lumens3Data.labels.push(entry.time); // Use time as x-axis label
                    lumens3Data.datasets[0].data.push(entry.lumens3);
                });

                // Update the chart for Lumens3
                lumens3Chart.update();
            })
            .catch(error => console.error('Error fetching Lumens3 data:', error));
    }

    // You can also handle the 'Enter' key press to trigger the function for Lumens3
    var lumens3DateInput = flatpickr("#lumens3-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        onChange: function (selectedDates, dateStr, instance) {
            // Call the updateLumens3Chart function when the date is selected for Lumens3
            updateLumens3Chart();
        }
    });

    // Initial update when the page loads for Lumens3
    updateLumens3Chart();
});
