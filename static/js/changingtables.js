  // Get references to the table header elements by their IDs
  const betsHeader = document.getElementById("betsHeader");
  const chatRoomHeader = document.getElementById("chatRoomHeader");
  const topWinnersHeader = document.getElementById("topWinnersHeader");
  const myBetsHeader = document.getElementById("myBetsHeader");

  // Get references to the table elements by their IDs
  const betTable = document.getElementById("bets-table");
  const chatRoomTable = document.getElementById("chat-room-table");
  const topWinnersTable = document.getElementById("top-winners-table");
  const myBetsTable = document.getElementById("my-bets-table");

  // Array of all header elements
  const headers = [betsHeader, chatRoomHeader, topWinnersHeader, myBetsHeader];

  // Array of all table elements
  const tables = [betTable, chatRoomTable, topWinnersTable, myBetsTable];

  // Function to reset background color for all headers and hide all tables
  function resetHeaderBackgroundAndHideTables() {
    for (const header of headers) {
      header.style.backgroundColor = 'gray';
    }
    for (const table of tables) {
      table.style.display = 'none';
    }
  }

  // Function to set the header width to 100%
  function setHeaderWidthTo100(header) {
    for (const header of headers) {
        header.style.width = '10%';
      }
    header.style.width = '100%';
  }

  // Add click event listeners to each header
  betsHeader.addEventListener("click", function () {
    resetHeaderBackgroundAndHideTables();
    betsHeader.style.backgroundColor = 'black';
    setHeaderWidthTo100(betsHeader);
    mirrorTableContent("bet-table-body", "bets-table-body");
    betTable.style.display = 'table'; // Show the "Bets" table
    console.log("Bets clicked");
  });

  chatRoomHeader.addEventListener("click", function () {
    resetHeaderBackgroundAndHideTables();
    chatRoomHeader.style.backgroundColor = 'black';
    setHeaderWidthTo100(chatRoomHeader);
    showChatRoom();
    chatRoomTable.style.display = 'table'; // Show the "Chat_room" table
    console.log("Chat_room clicked");
  });

  topWinnersHeader.addEventListener("click", function () {
    resetHeaderBackgroundAndHideTables();
    topWinnersHeader.style.backgroundColor = 'black';
    setHeaderWidthTo100(topWinnersHeader);

    showTopWinners();
    topWinnersTable.style.display = 'table'; // Show the "Top_winners" table
    console.log("Top_winners clicked");
  });

  myBetsHeader.addEventListener("click", function () {
    resetHeaderBackgroundAndHideTables();
    myBetsHeader.style.backgroundColor = 'black';
    setHeaderWidthTo100(myBetsHeader);
    showMyBets();
    myBetsTable.style.display = 'table'; // Show the "My Bets" table
    console.log("My Bets clicked");
  });

  function mirrorTableContent(sourceTableId, targetTableId) {
    const sourceTableBody = document.getElementById(sourceTableId);
    const targetTableBody = document.getElementById(targetTableId);

    // Clear the target table body
    targetTableBody.innerHTML = '';

    // Clone and append the rows from the source table to the target table
    for (const row of sourceTableBody.rows) {
      const newRow = row.cloneNode(true);
      targetTableBody.appendChild(newRow);
    }
  }
  function showChatRoom(){
    console.log('chat_room');
  }
  function showTopWinners() {
    // Make a GET request to fetch top winners data (replace 'yourApiEndpoint' with the actual endpoint)
    fetch(top_winners)
      .then(response => response.json())
      .then(data => {
        const tableBody = document.getElementById('top-winners-body');
  
        // Clear existing table rows
        tableBody.innerHTML = '';
  
        // Loop through the fetched data and add rows to the table
        if (Array.isArray(data)) {
        data.forEach(updatedItem => {
          const newRow = document.createElement('tr');
          newRow.innerHTML = `
            <td style="font-size: 0.6em;">${updatedItem.user}</td>
            <td style="font-size: 0.6em;">${updatedItem.bet}</td>
            <td style="font-size: 0.6em;">${updatedItem.multiplier}</td>
            <td style="font-size: 0.6em;">${parseFloat(updatedItem.won).toFixed(2)}</td>
            <td style="font-size: 0.6em;">${updatedItem.balloon}</td>
          `;
          tableBody.appendChild(newRow);
        });
    } else {
        // Handle non-array response (e.g., display an error message)
        console.error('Invalid data format from API:', data);
      }
      })
      .catch(error => {
        console.error('Error fetching top winners:', error);
      });
  }
  
  function showMyBets() {
    // Make a GET request to fetch top winners data (replace 'yourApiEndpoint' with the actual endpoint)
    fetch(my_bets)
      .then(response => response.json())
      .then(data => {
        const tableBody = document.getElementById('my-bets-body');
  
        // Clear existing table rows
        tableBody.innerHTML = '';
  
        // Loop through the fetched data and add rows to the table
        if (Array.isArray(data)) {
        data.forEach(updatedItem => {
          const newRow = document.createElement('tr');
         
          newRow.innerHTML = `
            <td style="font-size: 0.6em;">${updatedItem.created_at}</td>
            <td style="font-size: 0.6em;">${updatedItem.game_id}</td>
            <td style="font-size: 0.6em;">${parseFloat(updatedItem.stake).toFixed(2)}</td>
            <td style="font-size: 0.6em;">${parseFloat(updatedItem.multiplier).toFixed(2)}</td>
            <td style="font-size: 0.6em;">${updatedItem.balloon}</td>
            <td style="font-size: 0.6em;">${parseFloat(updatedItem.won).toFixed(2)}</td>

          `;
          tableBody.appendChild(newRow);
        });
    } else {
        // Handle non-array response (e.g., display an error message)
        console.error('Invalid data format from API:', data);
      }
      })
      .catch(error => {
        console.error('Error fetching my bets:', error);
      });
  }
  