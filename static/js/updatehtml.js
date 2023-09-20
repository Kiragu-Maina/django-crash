document.addEventListener('DOMContentLoaded', function() {
    const roomName = JSON.parse(document.getElementById('room-name').textContent);
    const socket = new WebSocket("wss://" + window.location.host + "/ws/table_updates/");  
    const socket2 = new WebSocket('wss://' + window.location.host + '/ws/balance_updates/');  
    const errorText = document.getElementById("error-text");
    var type;
    // Adjust the WebSocket URL
    const updateQueue = []; // Queue to hold update tasks

    // Function to process updates from the queue
    // async function processUpdateQueue() {
    //     while (updateQueue.length > 0) {
    //         const updateData = updateQueue.shift(); // Dequeue an update task
    //         if (updateData.type === "multiplier_update") {
    //             console.log(updateData);
    //             updateMultiplierAsync(updateData);
    //         }
    //     }
    // }
    socket.onmessage = async function (e) {
        const data = JSON.parse(e.data);
        console.log(data)
        if (data.type == "table_update") {
                console.log('updated items', data);
                type = 'won'
                updateTable(data, type);
            }
        else if (data.type == "bet_placed_update") {
                console.log('updated items', data);
                type = 'placed'
                updateTable(data, type);
                switch (data.balloon) {
                    case 'blue':
                        window.roomName = 'group_1'
                        break;
                    case 'red':
                        
                        window.roomName = 'group_2';
                        break;
                    case 'green':
                        
                        window.roomName = 'group_3';
                        break;
                    case 'purple':
                        
                        window.roomName = 'group_4';
                        break;
                    default:
                        console.log('Invalid group name: ' + groupName);
                        return; // Exit the function if the group name is invalid
                }
                
            }
        else if (data.type == "lose_update") {
                console.log('updated items', data);
                type = 'lost';
                
               await updateTableAsync(data, type);
            }
        else if (data.type == "new_game") {
            console.log(`newgame${data}`)
            const tableBody1 = document.getElementById('bet-table-body');
            tableBody1.innerHTML = '';
            errorText.innerHTML = '';
            
        }
        else if (data.type == "multiplier_update") {
            // Add the update task to the queue with a one-second delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            // updateQueue.push(data);
            updateMultiplier(data);
        
            // // If the queue was empty, start processing updates
            // if (updateQueue.length === 1) {
            //     processUpdateQueue();
            // }
        }
        else if (data.type == 'all_games_updates'){
            await new Promise(resolve => setTimeout(resolve, 1000));
            // updateQueue.push(data);
            updateAllGames(data);
        }
        
      
    }
    socket2.onmessage = async function (e) {
        const data = JSON.parse(e.data);
        if (data.type == "balance_update"){
        const updatedbalance = data
        console.log('updated balance', updatedbalance);
        await updateBalance(updatedbalance);
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
    async function updateTable(updatedItem, type) {
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
    
    async function updateBalance(updatedbalance) {
        const balance = document.getElementById('balance');
    
        balance.innerHTML = `Balance: ${parseFloat(updatedbalance.balance).toFixed(2)}`;
        
    }
    });
    async function updateTableAsync(updatedItem, type) {
        return new Promise((resolve) => {
            requestAnimationFrame(() => {
                updateTable(updatedItem, type).then(() => {
                    resolve();
                });
            });
        });
    }

    async function updateMultiplierAsync(updatedItem) {
        return new Promise((resolve) => {
            requestAnimationFrame(() => {
                updatemultiplier(updatedItem);
                resolve();
            });
        });
    }
    async function updateMultiplier(data) {
        const tableBody = document.getElementById('multiplier_row');
    
        if (data.multiplier) {
            // Create a new td element for the multiplier
            const maxVisibleTd = 10;

            // Select the table row
            
            // Get all td elements within the row
            const tdElements = tableBody.querySelectorAll('td');

          
                // Batched removal loop
                while (tdElements.length >= maxVisibleTd) {
                    
                        if (tdElements.length >= maxVisibleTd) {
                            tdElements[0].remove();
                            break;
                        }

                    
                    
            
                    
                }
            
       
            const newTd = document.createElement('td');
            const anchor = document.createElement('a');
            const span_element = document.createElement('span');
           
    
            // Set the font size and text content
            newTd.style.fontSize = '0.6em';
            newTd.style.border = '1px solid transparent';
            
            
            // Make the td clickable and open the modal when clicked
            anchor.onclick = () => {
                // Create and display the modal
                displayModal(data.group_name, data.server_seed, data.salt, data.hash);
            };
            anchor.href = "#provableModal";
            anchor.rel = "modal:open";
            anchor.style.textDecoration = "none";
            span_element.textContent = `x${data.multiplier}`;
            
    
            // Assign a random background color
            span_element.style.color = await getRandomColor();
            anchor.appendChild(span_element);
            newTd.appendChild(anchor);
            
    
            
            tableBody.appendChild(newTd);
            
        }
    }

    async function updateAllGames(data) {
        const tableBody2 = document.getElementById('concurrent-games-table');
    
        tableBody2.innerHTML = '';
        
        
        // Retrieve the multiplier based on the group_name
        
        const group = window.roomName; // Get the group_name from window.roomName
        console.log(group)
        switch (group) {
            case 'group_1':
                window.multiplier = parseFloat(data.group_1);
                break;
            case 'group_2':
                window.multiplier = parseFloat(data.group_2);
                break;
            case 'group_3':
                window.multiplier = parseFloat(data.group_3);
                break;
            case 'group_4':
                window.multiplier = parseFloat(data.group_4);
                break;
            default:
                window.multiplier = 1.0; // Default multiplier if group_name is not found
                break;
        }
        
        console.log(window.multiplier)
          
        
        const newRow = document.createElement('tr');
            
            
        tableBody2.innerHTML = `
            <td style="color:blue;">${data.group_1}</td>
            <td style="color:red;">${data.group_2}</td>
            <td style="color:green;">${data.group_3}</td>
            <td style="color:purple;">${data.group_4}</td>
            
        `;
            
    
            
            tableBody2.appendChild(newRow);
            
        }
    
    
    
    
    
    async function displayModal(groupName, serverSeed, salt, hash) {
        console.log('displayModal called');
        
        // Set modal content based on groupName
        let balloonColor = '';
        if (groupName === 'group_1') {
            balloonColor = 'blue';
        } else if (groupName === 'group_2') {
            balloonColor = 'red';
        } else if (groupName === 'group_3') {
            balloonColor = 'green';
        } else if (groupName === 'group_4') {
            balloonColor = 'purple';
        }
        
        // Set modal content dynamically
        $("#provableModal .modal-content").css("background-color", balloonColor);
        $("#balloon_name").text("Balloon:" + balloonColor);
        $("#serverSeed").text("Server Seed: " + serverSeed);
        $("#salt").text("Salt: " + salt);
        $("#hash").text("Hash: " + hash);
        
        // Show the modal
        $("#provableModal").show();
      
        // Close the modal when clicking the close button
        $(".close-modal").click(function() {
            $("#provableModal").hide();
        });
    }
    
    async function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }
    // Rest of your code...
    
    
 