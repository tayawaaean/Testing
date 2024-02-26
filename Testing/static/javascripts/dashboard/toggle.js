// Function to create a toggle group
function createToggleGroup(containerId) {
    let isLightOn = false;
    const container = document.getElementById(containerId);
    const toggleOnButton = container.querySelector('.toggleOn');
    const toggleOffButton = container.querySelector('.toggleOff');

    function updateButtonStyles() {
        toggleOnButton.style.backgroundColor = isLightOn ? '#12612b' : '#fff';
        toggleOnButton.style.color = isLightOn ? '#fff' : '#12612b';
        toggleOffButton.style.backgroundColor = isLightOn ? '#fff' : '#12612b';
        toggleOffButton.style.color = isLightOn ? '#12612b' : '#fff';
    }

    function toggleLight() {
        const message = isLightOn ? 'The light is already on. Are you sure you want to turn on the light?' : 'Are you sure you want to turn on the light?';
        Confirm.open({
            title: '',
            message: message,
            okText: 'Yes',
            cancelText: 'No',
            onok: () => {
                if (!isLightOn) {
                    console.log('You pressed yes! Light is now on.');
                } else {
                    console.log('You pressed yes! Light is still on.');
                }
                isLightOn = true;
                console.log('Light is on:', isLightOn);
                updateButtonStyles();
            },
            oncancel: () => {
                console.log(`You pressed no! Light remains ${isLightOn ? 'on' : 'off'}.`);
            }
        });
    }

    toggleOnButton.addEventListener('click', toggleLight);
    toggleOffButton.addEventListener('click', () => {
        if (!isLightOn) {
            Confirm.open({
                title: '',
                message: 'The light is already off.',
                okText: 'Ok',
                onok: () => {
                    console.log('You acknowledged that the light is already off.');
                }
            });
        } else {
            Confirm.open({
                title: '',
                message: 'Are you sure you want to turn off the light?',
                okText: 'Yes',
                cancelText: 'No',
                onok: () => {
                    console.log('You pressed yes! Light is now off.');
                    isLightOn = false;
                    console.log('Light is on:', isLightOn);
                    updateButtonStyles();
                },
                oncancel: () => {
                    console.log('You pressed no! Light remains on.');
                }
            });
        }
    });

    updateButtonStyles();
}

createToggleGroup('toggleContainer1');
createToggleGroup('toggleContainer2');
createToggleGroup('toggleContainer3');
createToggleGroup('toggleContainer4');