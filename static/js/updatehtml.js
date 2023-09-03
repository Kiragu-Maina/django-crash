document.addEventListener('DOMContentLoaded', function() {
const roomName = JSON.parse(document.getElementById('room-name').textContent);
const socket = new WebSocket("wss://" + window.location.host + "/ws/table_updates/");  
const socket2 = new WebSocket('wss://' + window.location.host + '/ws/balance_updates/');  
const errorText = document.getElementById("error-text");
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
function updateTable(updatedItem) {
    const tableBody = document.getElementById('bet-table-body');

    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td>${updatedItem.user}</td>
        <td>${updatedItem.bet}</td>
        <td>${updatedItem.multiplier}</td>
        <td>${parseFloat(updatedItem.won).toFixed(2)}</td>
    `;
    if (parseFloat(updatedItem.multiplier) !== 0) {
        newRow.style.backgroundColor = 'lightgreen'; // Set the background color
    }
    else if (parseFloat(updatedItem.multiplier) == 0) {
        newRow.style.backgroundColor = 'whitesmoke'; // Set the background color
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
