document.addEventListener('DOMContentLoaded', function () {
    // Initialize Chart.js for Lumens4
    var ctxLumens4 = document.getElementById('light2Chart').getContext('2d');
    var lumens4Data = {
        labels: [],
        datasets: [{
            label: 'Lumens4 Intensity',
            borderColor: 'black',
            data: [],
            fill: false,
        }]
    };

    var lumens4Chart = new Chart(ctxLumens4, {
        type: 'line',
        data: lumens4Data,
        options: {
            scales: {
                x: [{
                    type: 'linear',
                    position: 'bottom'
                }]
            }
        }
    });

    // Initialize flatpickr for Lumens4 date input
    flatpickr("#lumens4-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        defaultDate: "today", // Set the default date to today
    });

    // Function to update chart with data from the server for Lumens4
    function updateLumens4Chart() {
        // Get the selected date from the input for Lumens4
        var selectedDate = document.getElementById('lumens4-date-input').value;

        // Make an AJAX request to fetch Lumens4 data for the selected date from the server
        fetch('/get_lumens4_data_for_date/' + selectedDate)
            .then(response => response.json())
            .then(data => {
                // Clear existing data for Lumens4
                lumens4Data.labels = [];
                lumens4Data.datasets[0].data = [];

                // Populate chart data with fetched data
                data.forEach(entry => {
                    lumens4Data.labels.push(entry.time); // Use time as x-axis label
                    lumens4Data.datasets[0].data.push(entry.lumens4);
                });

                // Update the chart for Lumens4
                lumens4Chart.update();
            })
            .catch(error => console.error('Error fetching Lumens4 data:', error));
    }

    // You can also handle the 'Enter' key press to trigger the function for Lumens4
    var lumens4DateInput = flatpickr("#lumens4-date-input", {
        dateFormat: "Y-m-d",
        maxDate: "today", // Optional: Restrict selection to today and earlier
        onChange: function (selectedDates, dateStr, instance) {
            // Call the updateLumens4Chart function when the date is selected for Lumens4
            updateLumens4Chart();
        }
    });

    // Initial update when the page loads for Lumens4
    updateLumens4Chart();
});
