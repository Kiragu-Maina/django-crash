var isBalloonSelected = false;
var selectedBalloon = null; // Keep track of the currently selected balloon


// JavaScript function to handle balloon clicks and pass group names
function handleBalloonClick(groupName) {
    console.log('handle balloon clicked called')
    if (window.allowballoonchange) {
        if (selectedBalloon) {
            // Remove the "highlighted" class from the previously selected balloon
            selectedBalloon.classList.remove("highlighted");
        }

        var balloon;
        switch (groupName) {
            case 'group_1':
                balloon = document.getElementById('balloon1');
                window.roomName = 'group_1';
                break;
            case 'group_2':
                balloon = document.getElementById('balloon2');
                window.roomName = 'group_2';
                break;
            case 'group_3':
                balloon = document.getElementById('balloon3');
                window.roomName = 'group_3';
                break;
            case 'group_4':
                balloon = document.getElementById('balloon4');
                window.roomName = 'group_4';
                break;
            default:
                console.log('Invalid group name: ' + groupName);
                return; // Exit the function if the group name is invalid
        }

        // Set the "highlighted" class on the newly selected balloon
        balloon.classList.add("highlighted");
        selectedBalloon = balloon; // Update the selectedBalloon variable

        isBalloonSelected = true; // Set the flag to true
    }
}

// JavaScript function to remove the "highlighted" class on hover
function removeHighlight() {
    if (selectedBalloon) {
        selectedBalloon.classList.remove("highlighted");
    }
}
