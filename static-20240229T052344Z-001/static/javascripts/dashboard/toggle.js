function createToggleGroup(containerId, relay_num) {
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

    function toggleLight(action) {
        const message = isLightOn ? 'The light is already on. Are you sure you want to turn it off?' : 'The light is currently off. Are you sure you want to turn it on?';
        Confirm.open({
            title: '',
            message: message,
            okText: 'Yes',
            cancelText: 'No',
            onok: () => {
                $.get(`/turn_${action}/${relay_num}`, function(data, status){
                    console.log(`Light is now ${action === 'on' ? 'on' : 'off'}`);
                    isLightOn = action === 'on' ? true : false;
                    updateButtonStyles();
                    toggleSuccess(toggleOnButton);
                });
            },
            oncancel: () => {
                console.log(`You pressed no! Light remains ${isLightOn ? 'on' : 'off'}.`);
            }
        });
    }

    function toggleSuccess(button) {
        button.style.backgroundColor = '#6abf69'; // Change background color to green upon success
        setTimeout(() => {
            button.style.backgroundColor = isLightOn ? '#12612b' : '#fff'; // Reset background color after a short delay
        }, 1000); // Delay in milliseconds
    }

    toggleOnButton.addEventListener('click', () => toggleLight('on'));
    toggleOffButton.addEventListener('click', () => toggleLight('off'));

    updateButtonStyles();
}

createToggleGroup('toggleContainer1', 1);
createToggleGroup('toggleContainer2', 2);
createToggleGroup('toggleContainer3', 3);
createToggleGroup('toggleContainer4', 4);
