var isBalloonSelected = false;
var selectedBalloon = null; // Keep track of the currently selected balloon


// JavaScript function to handle balloon clicks and pass group names
function handleBalloonClick(groupName) {
	console.log('handle balloon clicked called')
	if (window.allowballoonchange) {
		// if (selectedBalloon) {
		// 	// Remove the "highlighted" class from the previously selected balloon
		// 	selectedBalloon.classList.remove("highlighted");
		// }

		var balloon;
		switch (groupName) {
			case 'group_1':
				// balloon = document.getElementById('balloon1');
				window.roomName = 'group_1';
				break;
			case 'group_2':
				// balloon = document.getElementById('balloon2');
				window.roomName = 'group_2';
				break;
			case 'group_3':
				// balloon = document.getElementById('balloon3');
				window.roomName = 'group_3';
				break;
			case 'group_4':
				// balloon = document.getElementById('balloon4');
				window.roomName = 'group_4';
				break;
			default:
				console.log('Invalid group name: ' + groupName);
				return; // Exit the function if the group name is invalid
		}

		// Set the "highlighted" class on the newly selected balloon
		// balloon.classList.add("highlighted");
		// selectedBalloon = balloon; // Update the selectedBalloon variable

		// isBalloonSelected = true; // Set the flag to true
	}
}

// JavaScript function to remove the "highlighted" class on hover
function removeHighlight() {
	if (selectedBalloon) {
		selectedBalloon.classList.remove("highlighted");
	}
}
function getCSRFToken() {
	var csrfMetaTag = document.querySelector('meta[name="csrf-token"]');
	if (csrfMetaTag) {
	  return csrfMetaTag.getAttribute('value');
	}
	return null; // Return null if the meta tag is not found
  }
  
  // Example usage:

function handleNewBalloonClick(groupName) {
    console.log('Handle balloon click called.');

    // Check if balloon clicking is allowed
    if (window.allowballooncrashlastbetting) {

        // Deselect the previously selected balloon, if any
        if (selectedBalloon) {
            selectedBalloon.classList.remove("highlighted");
        }

        // Find and select the balloon based on the provided groupName
        let balloon;
        switch (groupName) {
            case 'group_1':
                balloon = document.getElementById('new-balloonA');
                break;
            case 'group_2':
                balloon = document.getElementById('new-balloonB');
                break;
            case 'group_3':
                balloon = document.getElementById('new-balloonC');
                break;
            case 'group_4':
                balloon = document.getElementById('new-balloonD');
                break;
            default:
                console.log('Invalid group name: ' + groupName);
                return; // Exit the function if the group name is invalid
        }

        // Highlight the selected balloon and update the selectedBalloon variable
        balloon.classList.add("highlighted");
        selectedBalloon = balloon;
		console.log(groupName)

        // Flag that a balloon has been selected
        isBalloonSelected = true;
		const bet_amount = document.getElementById('selected-bet-amount').value;


        // Prepare data to send to the server
        // const data = {
        //     group_name: groupName,
		// 	bet_amount: bet_amount
        // };
		const formData = new FormData();
		formData.append('group_name', groupName);
		formData.append('bet_amount', bet_amount)
	
		var csrfToken = getCSRFToken();
		console.log('csrf_token is', csrfToken);

        // Send an AJAX POST request to the server
		fetch(betonlastballoon, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': csrfToken,

			},
			body: formData
		})
			.then(function (response) {
				if (response.ok) {
					return response.json();
				} else {
					throw new Error('Network response was not ok');
				}
			})
			.then(function (responseData) {
				// Handle the server response on success
				console.log('Response received:');
				console.log(responseData);
			})
			.catch(function (error) {
				// Handle errors on failure
				console.error('Error:', error);
				// Update the error message on the page
				document.getElementById("error1").innerHTML = "An error occurred.";
			});
        // Remove the highlight from the selected balloon after a delay
        
        // selectedBalloon.classList.remove("highlighted");
       
    }
}

// function sendlasttocrash(data, csrfToken){
// 	 // Send an AJAX POST request to the server
// 	 $.ajax({
// 		url: betonlastballoon,  // Replace with your actual login URL
// 		type: 'POST',
// 		data: data,
// 		success: function (response) {
// 			// Handle the response from the server, e.g., redirect or show a success message
// 			console.log(response);
			
			
// 		},
// 		error: function (xhr, status, error) {
// 			try {
// 			  var errorResponse = JSON.parse(xhr.responseText);
// 			  console.log(errorResponse)
// 			  var errorMessage = errorResponse.errors.__all__[0];
// 			  console.log(errorMessage);
// 			  $("#error2").html(errorMessage);
// 			} catch (e) {
// 				// Handle JSON parsing error or other issues
// 				console.error(e);
				
// 			}
		
// 		}
// 	});
// }