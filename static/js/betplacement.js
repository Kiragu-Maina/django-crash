
document.addEventListener('DOMContentLoaded', () => {
// Get all the amount buttons
	const amountButtons = document.querySelectorAll('.amount-btn');
	// Get the input field
	const selectedAmountInput = document.getElementById('selected-amount');
	const betButton = document.getElementById('bet-button');
	const errorText = document.getElementById('error-text');
	betButton.disabled = false;

	// Add click event listeners to each amount button
	amountButtons.forEach(button => {
		button.addEventListener('click', () => {
			// Get the data-amount attribute value from the button
			const amount = button.getAttribute('data-amount');
			// Update the input field value with the selected amount
			selectedAmountInput.value = amount;
			betButton.textContent = `BET (${amount})`;
		});
	});
	selectedAmountInput.addEventListener('input', () => {
		const selectedAmount = selectedAmountInput.value;
		betButton.textContent = `BET (${selectedAmount})`;
	});

	// Prevent the form from submitting when the "BET" button is clicked
	const betForm = document.getElementById('bet-form');
	const last_balloon_form =  document.getElementById('last-balloon-form');
	const betAmountInput = document.getElementById('betAmount');
	betAmountInput.value = selectedAmountInput.value;
	const hideErrorandResetBet = () => {
		errorText.style.display = 'none';
		errorText.innerHTML = '';
		betButton.textContent = 'BET';
	};

	betForm.addEventListener('submit', event => {
		event.preventDefault();

		const formData = new FormData();
		formData.append('bet_amount', selectedAmountInput.value);
		if (window.roomName) {
			formData.append('group_name', window.roomName);
		} else {
			formData.append('group_name', 'group_1');
		}

		const csrfToken = betForm.querySelector('[name=csrfmiddlewaretoken]').value;

		fetch(bet_placement, {
			method: 'POST',
			headers: {
				'X-CSRFToken': csrfToken,
			},
			body: formData,
		})
			.then(response => response.json())
			.then(data => {
				console.log('data sent', data);
				if (data.status == 'success') {
					window.globalBetAmount = parseFloat(data.bet_amount);
					betButton.textContent = 'BET Placed';
					betButton.disabled = true;
				} else {
					betButton.textContent = 'BET Not Placed';
					errorText.innerHTML = data.message;
					errorText.style.display = 'block';
					setTimeout(hideErrorandResetBet, 5000);
				}// Update the page content using the data received from the server
				// For example, update the user's balance or display a success message
			})
			.catch(error => {
				console.error('Error:', error);
			});

	});
	last_balloon_form.addEventListener('submit', event => {
		event.preventDefault();

		const bet_amount = document.getElementById('selected-bet2-amount').value;
		var groupName = document.getElementById('selected-balloon').value;


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
				'X-CSRFToken': csrfToken,
			},
			body: formData,
		})
			.then(response => response.json())
			.then(data => {
				console.log('data sent', data);
				if (data.status == 'success') {
					window.globalBetAmount = parseFloat(data.bet_amount);
					betButton.textContent = 'BET Placed';
					betButton.disabled = true;
				} else {
					betButton.textContent = 'BET Not Placed';
					errorText.innerHTML = data.message;
					errorText.style.display = 'block';
					setTimeout(hideErrorandResetBet, 5000);
				}// Update the page content using the data received from the server
				// For example, update the user's balance or display a success message
			})
			.catch(error => {
				console.error('Error:', error);
			});
		});
		function getCSRFToken() {
			console.log('getcsrftokencalled');
			var csrfTokenDiv = document.getElementById("csrf_token");
			var csrfToken = csrfTokenDiv.querySelector("[name=csrfmiddlewaretoken]").value;	  
			return csrfToken; // Return null if the meta tag is not found
		}
		

});
