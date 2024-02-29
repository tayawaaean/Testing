let monthYearSelected;
let currentTemp = 17;
let value = "off";
let rackNumber;

document.querySelector('#dycalendar').addEventListener('click', function(event) {
    if (event.target.tagName === 'TD') { // Check if the clicked element is a <td>
        var clickedCellClass = event.target.className;
        
        var tdContainer = document.getElementById('dycalendar');
        var tdElements = tdContainer.querySelectorAll('td');
        var displayContainer = document.querySelector('#displayContainer');
        var monthYear = document.querySelector(".dycalendar-span-month-year");
        var numberOfTds = tdElements.length;
        var dateSelected = null;
        const textmonthYear = monthYear.textContent;

        for(let i= 1; i < numberOfTds; i++){
            if(clickedCellClass == 'date' + i){
                dateSelected = i;
                break;
            }
            else if(clickedCellClass == 'date'+ i +' dycalendar-today-date'){
                dateSelected = i;
                break; 
            }
        }
        if (dateSelected != null){
            displayContainer.textContent = dateSelected + " " + textmonthYear;
        }
        monthYearSelected = dateSelected + ' ' + textmonthYear;
    }
});

dycalendar.draw({
    target: '#dycalendar',
    type: 'month', 
    prevnextbutton: 'show' ,
    highlighttoday: true, 
});

//Time Setting Schedule

let timerRef = document.querySelector('#displayTime');
const hourInput = document.getElementById('hourInput');
const minuteInput = document.getElementById('minuteInput');
const hourInput2 = document.getElementById('hourInput2');
const minuteInput2 = document.getElementById('minuteInput2');
const setAlarm = document.getElementById('set');
const activeAlarms = document.querySelector(".activeAlarms");


let alarmArray=[];

let initialHour = 0, initialMinute = 0, alarmIndex = 0;

const appendZero = (value) => (value < 10? "0" + value : value);

const searchObject = (parameter, value ) => {
    let alarmObject, 
        objIndex, 
        exists = false;
    alarmsArray.forEach((alarm, index) => {
        if (alarm[parameter] == value){
            exists = true;
            alarmObject = alarm;
            objIndex = index;
            return false;
        } 
    });
    return [exists, alarmObject, objIndex];
};

const isCurrentTimeInRange = (currentTime, startTime, endTime) => {
    return currentTime >= startTime && currentTime <= endTime;
};

//display time
function displayTime(){
    let date = new Date();
    let [hours, minutes, seconds] = [
        appendZero(date.getHours()),
        appendZero(date.getMinutes()),
        appendZero(date.getSeconds()),
    ];
    let ampm = hours >= 12 ? 'PM' : 'AM';

    // Convert to 12-hour format
    hours = hours % 12 || 12;

    timerRef.innerHTML = `${hours}:${minutes}:${seconds} ${ampm}`;

    alarmsArray.forEach((alarm, index) => {
        if (alarm.isActive) {
          if (`${alarm.alarmHour}:${alarm.alarmMinute}` === `${hours}:${minutes}`) {
            alert("Schedule Met!");
          }
        }
    });
}

const inputCheck = (inputValue) => {
    inputValue = parseInt(inputValue);
    if (inputValue < 10) {
        inputValue = appendZero(inputValue);
    }
    return inputValue;
};

hourInput.addEventListener("input", () => {
    hourInput.value = inputCheck(hourInput.value);
});
minuteInput.addEventListener("input", () => {
    minuteInput.value = inputCheck(minuteInput.value);
});

hourInput2.addEventListener("input", () => {
    hourInput2.value = inputCheck(hourInput2.value);
});
minuteInput2.addEventListener("input", () => {
    minuteInput2.value = inputCheck(minuteInput2.value);
});


const createAlarm = (alarmObj) => {
    // Keys from object
    const { id, monthYearSelected, alarmHour, alarmMinute, alarmHour2, alarmMinute2 } = alarmObj;
    const insertingModal = document.getElementById('insertingModal');
    insertingModal.style.display = 'block';

    // Alarm div
    let alarmDiv = document.createElement("div");
    alarmDiv.classList.add("alarm");
    alarmDiv.setAttribute("data-id", id);
    alarmDiv.innerHTML = `
        <div class="notification">
            <div class="content">
                <div class="info">
                    <h3 class='alarmhead'>${monthYearSelected}</h3>
                    <p>
                        Time: ${alarmHour}:${alarmMinute}-${alarmHour2}:${alarmMinute2}
                    </p>
                    <small class="text_muted">
                        Grow Lights: ${value} | Temperature: ${currentTemp} °C | Rack Number: ${rackNumber}
                    </small>
                </div>
                <span class= Dbutton>
                    <button class="deleteButton" onclick="deleteAlarm(event)">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </span>
            </div>
        </div>
    `;

    activeAlarms.appendChild(alarmDiv);

    // Send alarm data to the server
    fetch('/insert_schedule_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            monthYearSelected: monthYearSelected,
            rack: rackNumber,
            time_start: `${alarmHour}:${alarmMinute}`,
            time_end: `${alarmHour2}:${alarmMinute2}`,
            temperature: currentTemp,
            grow_light_status: value,
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Hide the inserting modal
        insertingModal.style.display = 'none';

        if (data.success) {
            // Show success message
            alert('Schedule is Set');

            // You can perform any additional actions here based on the server response.
            // For example, update UI or handle other business logic.

            window.location.reload();

        } else {
            console.error('Failed to send alarm data:', data.error);
            alert('Inserting... Failed!');
        }
    })
    .catch(error => {
        console.error('Error while sending alarm data:', error);
        alert('Inserting... Error!');
    });
};



//Set Alarm
setAlarm.addEventListener("click", () => {
    alarmIndex += 1;
    //alarmObject
    let alarmObj = {};
    alarmObj.id = `${alarmIndex}_${hourInput.value}_${minuteInput.value}_${hourInput2.value}_${minuteInput2.value}`;
    alarmObj.monthYearSelected = monthYearSelected;
    alarmObj.alarmHour = hourInput.value;
    alarmObj.alarmMinute = minuteInput.value;
    alarmObj.alarmHour2 = hourInput2.value;
    alarmObj.alarmMinute2 = minuteInput2.value;
    alarmObj.isActive = false;
    console.log(alarmObj);
    alarmsArray.push(alarmObj);
    if(monthYearSelected != null){
        createAlarm(alarmObj);
        hourInput.value = appendZero(initialHour);
        minuteInput.value = appendZero(initialMinute);
        hourInput2.value = appendZero(initialHour);
        minuteInput2.value = appendZero(initialMinute);
    }else{
        alert("No date!");
        hourInput.value = appendZero(initialHour);
        minuteInput.value = appendZero(initialMinute);
        hourInput2.value = appendZero(initialHour);
        minuteInput2.value = appendZero(initialMinute);
    }
});

//Start Alarm
const startAlarm = (e) => {
    let searchId = e.target.parentElement.getAttribute("data-id");
    let [exists, obj, index] = searchObject("id", searchId);
    if (exists) {
      alarmsArray[index].isActive = true;
    }
};
  //Stop alarm
  const stopAlarm = (e) => {
    let searchId = e.target.parentElement.getAttribute("data-id");
    let [exists, obj, index] = searchObject("id", searchId);
    if (exists) {
      alarmsArray[index].isActive = false;
      alarmSound.pause();
    }
};

const deleteAlarm = (e) => {
    let searchId = e.target.parentElement.parentElement.parentElement.parentElement.parentElement.getAttribute("data-id");
    let [exists, obj, index] = searchObject("id", searchId);
    if (exists) {
      e.target.parentElement.parentElement.parentElement.parentElement.parentElement.remove();
      alarmsArray.splice(index, 1);
    }
    console.log(searchId);
};



window.onload = () => {
    setInterval(displayTime);
    initialHour = 0;
    initialMinute = 0;
    alarmIndex = 0;
    alarmsArray = [];
    hourInput.value = appendZero(initialHour);
    minuteInput.value = appendZero(initialMinute);
    hourInput2.value = appendZero(initialHour);
    minuteInput2.value = appendZero(initialMinute);
};

function updateTemp() {
    document.getElementById('temp').innerText = currentTemp;
}

function increaseTemp() {
    if(currentTemp < 32){
        currentTemp++;
        console.log(currentTemp);
        updateTemp();
    }
}

function decreaseTemp() {
    if(currentTemp > 17){
        currentTemp--;
        console.log(currentTemp);
        updateTemp();
    }
}

function toggleSwitchChanged() {
    let toggleSwitch = document.getElementById("myToggle");
    value = toggleSwitch.checked ? "on" : "off";
    console.log(value);
}

function getSelectedRack() {
    let selectElement = document.getElementById("racks");
    let selectedValue = selectElement.value;
    rackNumber = selectedValue;
    console.log(rackNumber);
}