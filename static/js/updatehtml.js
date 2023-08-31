document.addEventListener('DOMContentLoaded', function() {
const roomName = JSON.parse(document.getElementById('room-name').textContent);
const socket = new WebSocket("wss://" + window.location.host + "/ws/table_updates/");  
const socket2 = new WebSocket('wss://' + window.location.host + '/ws/balance_updates/');  

// Adjust the WebSocket URL

socket.onmessage = async function (e) {
    const data = JSON.parse(e.data);
    if (data.type == "table_update") {
            console.log('updated items', data);
            updateTable(data);
        }
    else if (data.type == "new_game") {
        const hash = data.game_hash
        const tableBody = document.getElementById('bet-table-body');
        tableBody.innerHTML = '';
    }
}
socket2.onmessage = function (event) {
    const updatedbalance = JSON.parse(event.data);
    console.log('updated balance', updatedbalance);
    updateBalance(updatedbalance);
};

function updateTable(updatedItem) {
    const tableBody = document.getElementById('bet-table-body');

    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td>${updatedItem.user}</td>
        <td>${updatedItem.bet}</td>
        <td>${updatedItem.multiplier}</td>
        <td>${updatedItem.won}</td>
    `;
    if (parseFloat(updatedItem.multiplier) !== 0) {
        newRow.style.backgroundColor = 'lightgreen'; // Set the background color
    }

    if (tableBody.firstChild) {
        tableBody.insertBefore(newRow, tableBody.firstChild);
    } else {
        tableBody.appendChild(newRow);
    }
}

function updateBalance(updatedbalance) {
    const balance = document.getElementById('balance');

    balance.innerHTML = `Balance: ${updatedbalance.balance}`;
    
}
});