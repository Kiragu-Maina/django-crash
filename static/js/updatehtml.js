document.addEventListener('DOMContentLoaded', function() {
const roomName = JSON.parse(document.getElementById('room-name').textContent);
const socket = new WebSocket("wss://" + window.location.host + "/ws/table_updates/");  
const socket2 = new WebSocket('wss://' + window.location.host + '/ws/balance_updates/');  
const errorText = document.getElementById("error-text");
var type;
// Adjust the WebSocket URL

socket.onmessage = async function (e) {
    const data = JSON.parse(e.data);
    if (data.type == "table_update") {
            console.log('updated items', data);
            type = 'won'
            updateTable(data, type);
        }
    else if (data.type == "bet_placed_update") {
            console.log('updated items', data);
            type = 'placed'
            updateTable(data, type);
        }
    else if (data.type == "lose_update") {
            console.log('updated items', data);
            type = 'lost'
            
            updateTable(data, type);
        }
    else if (data.type == "new_game") {
        const hash = data.game_hash
        const tableBody = document.getElementById('bet-table-body');
        tableBody.innerHTML = '';
        errorText.innerHTML = '';
    }
}
socket2.onmessage = async function (e) {
    const data = JSON.parse(e.data);
    if (data.type == "balance_update"){
    const updatedbalance = data
    console.log('updated balance', updatedbalance);
    updateBalance(updatedbalance);
    }
    else if (data.type == "cashout"){
        
        errorText.innerHTML = data.message;
        errorText.style.display = 'block';
        setTimeout(hideErrorandResetBet, 5000); 

    }
};
 const hideErrorandResetBet = () => {
                      errorText.style.display = 'none';
                      errorText.innerHTML = '';
                      
                  };
function updateTable(updatedItem, type) {
    const tableBody = document.getElementById('bet-table-body');

    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td style="font-size: 0.6em;">${updatedItem.user}</td>
        <td style="font-size: 0.6em;">${updatedItem.bet}</td>
        <td style="font-size: 0.6em;">${updatedItem.multiplier}</td>
        <td style="font-size: 0.6em;">${parseFloat(updatedItem.won).toFixed(2)}</td>
        <td style="font-size: 0.6em;">${updatedItem.balloon}</td>
    `;
    if (type == 'won') {
        newRow.style.backgroundColor = 'lightgreen'; // Set the background color
    }
    else if (type == 'placed') {
        newRow.style.backgroundColor = 'whitesmoke'; // Set the background color
    }
    else if (type == 'lost') {
        newRow.style.backgroundColor = 'red'; // Set the background color
    }

    if (tableBody.firstChild) {
        tableBody.insertBefore(newRow, tableBody.firstChild);
    } else {
        tableBody.appendChild(newRow);
    }
}

function updateBalance(updatedbalance) {
    const balance = document.getElementById('balance');

    balance.innerHTML = `Balance: ${parseFloat(updatedbalance.balance).toFixed(2)}`;
    
}
});
