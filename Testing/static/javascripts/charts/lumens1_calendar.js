document.addEventListener('DOMContentLoaded', function () {
    // Calendar variables
    var calendarContainer = document.getElementById('lumens1-container');
    var calendarInput = document.getElementById('calendar-input');
    var calendarDropdown = document.getElementById('calendar-dropdown');
    var monthDropdown = document.getElementById('month-dropdown');
    var yearDropdown = document.getElementById('year-dropdown');

    // Initialize calendar
    initializeCalendar();

    
    // Function to initialize the calendar
    function initializeCalendar() {
        // Populate month dropdown
        var months = [
            'January', 'February', 'March', 'April',
            'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December'
        ];
        for (var i = 0; i < months.length; i++) {
            var option = document.createElement('option');
            option.value = i + 1;
            option.text = months[i];
            monthDropdown.add(option);
        }

        // Populate year dropdown (adjust range as needed)
        var currentYear = new Date().getFullYear();
        for (var year = currentYear - 5; year <= currentYear + 5; year++) {
            var option = document.createElement('option');
            option.value = year;
            option.text = year;
            yearDropdown.add(option);
        }

        // Set initial values
        var currentDate = new Date();
        monthDropdown.value = currentDate.getMonth() + 1;
        yearDropdown.value = currentDate.getFullYear();

        // Update calendar based on input date
        updateCalendar();

        // Show/hide calendar dropdown
        calendarInput.addEventListener('click', function () {
            calendarDropdown.style.display = 'block';
        });

        // Close calendar dropdown when clicking outside
        window.addEventListener('click', function (event) {
            if (!calendarContainer.contains(event.target)) {
                calendarDropdown.style.display = 'none';
            }
        });
    }

    // Function to update calendar based on selected month and year
    function updateCalendar() {
        var selectedMonth = monthDropdown.value;
        var selectedYear = yearDropdown.value;

        var daysInMonth = new Date(selectedYear, selectedMonth, 0).getDate();
        var options = '';
        for (var i = 1; i <= daysInMonth; i++) {
            options += '<option value="' + i + '">' + i + '</option>';
        }

        // Clear existing options and add new ones
        calendarInput.innerHTML = '';
        calendarInput.innerHTML += options;

        // Close calendar dropdown after updating
        calendarDropdown.style.display = 'none';
    }

    // Function to navigate to the previous month
    function prevMonth() {
        var currentMonth = parseInt(monthDropdown.value, 10);
        var currentYear = parseInt(yearDropdown.value, 10);

        if (currentMonth > 1) {
            monthDropdown.value = currentMonth - 1;
        } else {
            monthDropdown.value = 12;
            yearDropdown.value = currentYear - 1;
        }

        updateCalendar();
    }

    // Function to navigate to the next month
    function nextMonth() {
        var currentMonth = parseInt(monthDropdown.value, 10);
        var currentYear = parseInt(yearDropdown.value, 10);

        if (currentMonth < 12) {
            monthDropdown.value = currentMonth + 1;
        } else {
            monthDropdown.value = 1;
            yearDropdown.value = currentYear + 1;
        }

        updateCalendar();
    }

    // Function to close the calendar dropdown
    function closeCalendar() {
        calendarDropdown.style.display = 'none';
    }
})