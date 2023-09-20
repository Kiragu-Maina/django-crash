document.addEventListener('DOMContentLoaded', function() {
    
    const socket = new WebSocket("wss://" + window.location.host + "/ws/admin_updates/");  
  
    
    // Adjust the WebSocket URL
    
    socket.onmessage = async function (e) {
        const data = JSON.parse(e.data);
        if (data.type == "new_update") {
                console.log('updated items', data);
                updateTable(data);
            }
        
    }
    
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
        }
        else if (parseFloat(updatedItem.multiplier) == 0) {
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
    