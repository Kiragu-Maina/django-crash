function hasPageParameter(pageParameter) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.has(pageParameter);
}

  function checkAndCallToggleWithdrawals() {
	if (hasPageParameter('deposits_page')) {
		toggleSection('deposits');
		
	} else if (hasPageParameter('withdrawals_page')) {
		toggleSection('withdrawals');
		
	} 
	else if (hasPageParameter('bets_page')) {
		toggleSection('betspage');
		
	} else if (hasPageParameter('users_page')) {
		toggleSection('userspage');
		
	} else if (hasPageParameter('admins_page')) {
		toggleSection('adminspage');
	
	}
	else {

	}
	
  }
  
  // Call the function when the page loads
  window.addEventListener('load', function () {
	checkAndCallToggleWithdrawals(); 
  });
  

document.addEventListener('DOMContentLoaded', () => {
	
	const socket = new WebSocket('wss://' + window.location.host + '/ws/admin_updates/');

	// Adjust the WebSocket URL

	socket.onmessage = async function (e) {
		const data = JSON.parse(e.data);
		if (data.type === 'new_update') {
			console.log('updated items', data);
			updateTable(data);
		} else if (data.type === 'player_update') {
			console.log('updated items', data);
			updateplayercount(data);
		}
	};

	function updateTable(updatedItem) {
		const tableBody = document.getElementById('bet-table-body');
		const pot = document.getElementById('pot');
		const profit = document.getElementById('profit');
		const revenue = document.getElementById('revenue');

		const newRow = document.createElement('tr');

		newRow.innerHTML = `
                
                <td style="font-size: 0.6em;">${parseFloat(updatedItem.total_cash).toFixed(2)}</td>
                
                <td style="font-size: 0.6em;">${parseFloat(updatedItem.users_cash).toFixed(2)}</td>
                <td style="font-size: 0.6em;">${parseFloat(updatedItem.float_cash).toFixed(2)}</td>
                <td style="font-size: 0.6em;">${parseFloat(updatedItem.profit).toFixed(2)}</td>

                
                
                
            `;

		if (parseFloat(updatedItem.multiplier) !== 0) {
			newRow.style.backgroundColor = 'lightgreen'; // Set the background color
		} else if (parseFloat(updatedItem.multiplier) == 0) {
			newRow.style.backgroundColor = 'whitesmoke'; // Set the background color
		}

		if (tableBody.firstChild) {
			tableBody.insertBefore(newRow, tableBody.firstChild);
		} else {
			tableBody.appendChild(newRow);
		}

		pot.innerHTML = `Pot: ${parseFloat(updatedItem.total_cash).toFixed(2)}`;
		revenue.innerHTML = `Revenue: ${parseFloat(updatedItem.revenue).toFixed(2)}`;
		profit.innerHTML = `Profit: ${parseFloat(updatedItem.profit).toFixed(2)}`;
	}
	
});
function toggleSection(sectionName) {
	console.log('toggleSection called');
	const sections = {
	  "dashboard": document.getElementById("dashboard"),
	  "control-game": document.getElementById("control-game"),
	  "withdrawals": document.getElementById("withdrawals"),
	  "deposits": document.getElementById("deposits"),
	  "userspage": document.getElementById("userspage"),
	  "betspage": document.getElementById("betspage"),
	  "adminspage": document.getElementById("adminspage")
	};
  
	// Corrected variable declarations
	const dashboard_span = document.getElementById("show-dashboard-span");
	const control_game_span = document.getElementById("show-control-game-span");
	const withdrawals_span = document.getElementById("show-withdrawals-span");
	const deposits_span = document.getElementById("show-deposits-span");
	const userspage_span = document.getElementById("show-userspage-span");
	const betspage_span = document.getElementById("show-betspage-span");
	const adminspage_span = document.getElementById("show-adminspage-span");
  
	const section = sections[sectionName];
  
	if (section) {
	  section.style.display = 'block';
	  // Corrected text-decoration style assignment
	  if (sectionName === "dashboard") dashboard_span.style.textDecoration = 'underline';
	  if (sectionName === "control-game") control_game_span.style.textDecoration = 'underline';
	  if (sectionName === "withdrawals") withdrawals_span.style.textDecoration = 'underline';
	  if (sectionName === "deposits") deposits_span.style.textDecoration = 'underline';
	  if (sectionName === "userspage") userspage_span.style.textDecoration = 'underline';
	  if (sectionName === "betspage") betspage_span.style.textDecoration = 'underline';
	  if (sectionName === "adminspage") adminspage_span.style.textDecoration = 'underline';
	}
  
	for (const key in sections) {
	  if (sections.hasOwnProperty(key) && key !== sectionName && sections[key] !== null) {
		sections[key].style.display = 'none';
		// Corrected text-decoration style assignment
		if (key === "dashboard") dashboard_span.style.textDecoration = 'none';
		if (key === "control-game") control_game_span.style.textDecoration = 'none';
		if (key === "withdrawals") withdrawals_span.style.textDecoration = 'none';
		if (key === "deposits") deposits_span.style.textDecoration = 'none';
		if (key === "userspage") userspage_span.style.textDecoration = 'none';
		if (key === "betspage") betspage_span.style.textDecoration = 'none';
		if (key === "adminspage") adminspage_span.style.textDecoration = 'none';
	  }
	}
  }
  

function updateplayercount(updatedItem) {

	const players_online = document.getElementById('players_online');
	const players_in_current_game = document.getElementById('players_in_current_game');
	const players_winning = document.getElementById('players_winning');
	const players_losing = document.getElementById('players_losing');
	players_online.innerHTML =`Players online: ${updatedItem.players_online}`;
	players_in_current_game.innerHTML = `Players betting: ${updatedItem.players_betting}`;
	players_winning.innerHTML = `Players who cashed out: ${updatedItem.players_won}`;
	players_losing.innerHTML = `Players who lost: ${updatedItem.players_lost}`;
}

