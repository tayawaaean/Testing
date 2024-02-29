document.addEventListener('DOMContentLoaded', function () {
    // Function to fetch the latest entry from the ac_control collection
    function fetchLatestACControlledBy() {
        // Make an HTTP request to your backend to fetch the latest entry
        fetch('/latest_ac_control')
            .then(response => response.json())
            .then(data => {
                // Update the content of the h2 element with the latest controlled_by information
                document.getElementById('userDisplayac').innerText = `Currently controlled by: ${data.controlled_by}`;
            })
            .catch(error => console.error('Error fetching latest AC control:', error));
    }

    // Call the fetchLatestACControlledBy function when the DOM content is loaded
    fetchLatestACControlledBy();
});

document.addEventListener('DOMContentLoaded', function () {
    // Function to fetch the latest entry from the light_toggle collection
    function fetchLatestControlledBy() {
        // Make an HTTP request to your backend to fetch the latest entry
        fetch('/latest_controlled_by')
            .then(response => response.json())
            .then(data => {
                // Loop through each rack number and update the corresponding userDisplay element
                for (let i = 1; i <= 4; i++) {
                    const rackNumber = i;
                    const userDisplayId = `userDisplay${rackNumber}`;
                    const userDisplayElement = document.getElementById(userDisplayId);
                    if (userDisplayElement) {
                        userDisplayElement.innerText = `Currently controlled by: ${data[rackNumber] || 'Unknown'}`;
                    }
                }
            })
            .catch(error => console.error('Error fetching latest controlled_by:', error));
    }

    // Call the fetchLatestControlledBy function when the DOM content is loaded
    fetchLatestControlledBy();
});