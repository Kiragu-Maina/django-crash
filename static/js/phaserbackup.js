

class Example extends Phaser.Scene 
    
{
   

    preload ()
    {
        this.load.image('balloon', balloon);
        


        this.load.image('bg', space);
        this.load.image('pumpUp', pumpup);
        this.load.image('pumpDown', pumpdown);
        
        this.load.image('popped', popped);
       
        
        this.load.bitmapFont('desyrel', 'https://labs.phaser.io/assets/fonts/bitmap/desyrel.png', 'https://labs.phaser.io/assets/fonts/bitmap/desyrel.xml');
    }

   async create ()
    {
        
        
        console.log('create called');
        const scene = this;
        let backg = scene.add.image(400, 300, 'bg');

        const loading_game = scene.add.text(400, 28, 'Game loading....').setColor('#00ff00').setFontSize(32).setShadow(2, 2).setOrigin(0.5, 0);
        
        
        
       
        async function main(scene) {
            try {
                
                const wsSocket = new WebSocket("ws://" + window.location.host + "/ws/realtime/");
                // const wsSocket = new WebSocket('ws://'
                // + window.location.host
                // + '/ws/real_time_updates/'
                // + 'group_1'
                // + '/');
                let isCrashTriggered = false; 
             
                // scene.add.sprite(400, 300, 'background').play('explodeAnimation');
                
                let currentImage = 'pumpUp'; // Start with 'pump up'
                let balloonsTween = null;
                let lightsTween = null;
                const graph = scene.add.graphics();
                let delay = 200; // Delay in milliseconds (0.1 seconds)
               
        
               
        
                const centerX = 400;
                const centerY = 500;
        
                // Create a strong point line
                const graphics = scene.add.graphics({ lineStyle: { width: 6, color: 0x0000ff  } });
               
               
               
               
        
        
               

                

                

                
                
                
                // const counterText = scene.add.dynamicBitmapText(400, 200, 'desyrel', '0.00').setOrigin(0.5, 0);
                
                
                let crashInstructionProcessed = false;
                let countAndDisplayTimer;   
                let continueCounting = true;
                const delayTime = 10;    
                let counterText;
                let countdownText;
                let crashText;
                let bet_allowed_text;
                let cashoutclicked = false;
               
                
                
                
                
                let start = true;
                const betButton = document.getElementById("bet-button");
                let game_id;
                let balloons;
                let light;
                let poppedbackground;
                let pump;
                let Line;
                let animationTimer;
                let start_initial = true;
                let roomName;
                let groupSocket;
                let chooseballoontext;
                let ballooncount;
                let start_with_balloon = true;
                let showballoons = true;

                

                wsSocket.onmessage = async function (e) {
                    console.log('received message');

                    if(loading_game){
                      loading_game.destroy();
                    }
                        const data = JSON.parse(e.data);
                        console.log(data.type);
                        if (data.type == "ongoing_synchronizer") {
                            // Use the current multiplier to render the ongoing graph
                            const currentMultiplier = data.cached_multiplier; // Assuming the currentMultiplier is provided in the data
                            // Use currentMultiplier to render the ongoing graph
                            console.log('ongoing synchronizer');
                            countAndDisplayOngoing(currentMultiplier);
                           
                            console.log(data)
                        }
                        
                        
                        

                        else if (data.type == "start_synchronizer") {
                                window.allowballoonchange = true;
                                showballoons = true;
                            
                            // Start the synchronizer countdown
                               console.log('start_synchronizer');
                                if (counterText) {
                                    counterText.destroy();
                                }
                                if (bet_allowed_text) {
                                    bet_allowed_text.destroy();
                                }
                                if (poppedbackground) {
                                    // Destroy the existing background image
                                    poppedbackground.destroy();
                                }
                               
    
                                backg = scene.add.image(400, 300, 'bg').setPipeline('Light2D');
                                console.log(data.count);
                                const delay = 1000;  // Delay in milliseconds
                                const updateInterval =1;
                                const crashPoint = 15; // Adjust this value as needed
                                chooseballoontext = scene.add.dynamicBitmapText(400, 200, 'desyrel').setOrigin(0.5, 0);
                                
                                
                                    let count = 15;
                                    // Define the minimum countdown value (0 seconds)
                                    const minCountdown = 0;

                                    while (count >= minCountdown) {
                                        if (showballoons) {
                                            showballoons = false;
                                        
                                            // Use jQuery to create a modal and add balloons inside it
                                            var $modal = $('<div id="balloonModal">');
                                        
                                            // Add CSS styles to position the balloons horizontally
                                            $modal.css({
                                                'display': 'flex',
                                                'justify-content': 'space-between',
                                                'align-items': 'center',
                                                'border-radius': '15px', // Adjust the border-radius for curvy borders
                                                'background-color': 'rgba(0, 0, 0, 0.7)', // Adjust the alpha value for transparency
                                                'padding': '20px', // Add some padding to the modal
                                                'box-shadow': '0px 0px 10px 2px rgba(0,0,0,0.5)', // Add a shadow for depth
                                                'color': 'white', // Set text color to white
                                            });
                                        
                                            // Define the colors for the second, third, and fourth balloons
                                            var balloonColors = ['2', '3', '4'];
                                            var $selectedBalloon = null;
                                        
                                            for (var i = 0; i < 4; i++) {
                                                var color = i === 0 ? '' : balloonColors[i - 1];
                                                var balloonImage = balloon.replace('.png', color + '.png');
                                                var $balloon = $('<div class="balloon"><img src="' + balloonImage + '" alt="Balloon ' + (i + 1) + '"></div>');
                                                $balloon.css({
                                                    'width': '50px',
                                                    'height': '100px',
                                                    'margin': '5px',
                                                    'cursor': 'pointer' // Add cursor pointer for indicating it's clickable
                                                });
                                        
                                                // Add a click event handler to the balloon
                                                $balloon.click(function (event) {
                                                    event.preventDefault();
                                                    var balloonNumber = $(this).find('img').attr('alt').split(' ')[1];
                                        
                                                    if (![2, 3, 4].includes(parseInt(balloonNumber))) {
                                                        balloonNumber = '1';
                                                    }
                                        
                                                    handleBalloonClicked(balloonNumber, $(this));
                                                });
                                        
                                                $modal.append($balloon);
                                            }
                                        
                                            // Append the modal to the body
                                            $('body').append($modal);
                                        
                                            // Open the modal
                                            $modal.dialog({
                                                modal: true,
                                                title: 'Choose Balloon:',
                                                width: 'auto',
                                               
                                                close: function (event, ui) {
                                                    // This function is executed when the dialog is closed.
                                                    // You can perform any cleanup or post-closing actions here.
                                                    $(this).dialog('destroy').remove();
                                                }
                                            });
                                        
                                            // Function to handle balloon click outside the if (showballoons) block
                                            function handleBalloonClicked(balloonNumber, $clickedBalloon) {
                                                // Remove highlight from previously selected balloon
                                                if ($selectedBalloon) {
                                                    $selectedBalloon.css('background-color', '');
                                                }
                                        
                                                // Highlight the clicked balloon
                                                $clickedBalloon.css('background-color', 'yellow');
                                                $selectedBalloon = $clickedBalloon;
                                                switch (balloonNumber) {
                                                    case '1':
                                                        handleBalloonClick('group_1');
                                                        break;
                                                    case '2':
                                                        handleBalloonClick('group_2');
                                                        break;
                                                    case '3':
                                                        handleBalloonClick('group_3');
                                                        break;
                                                    case '4':
                                                        handleBalloonClick('group_4');
                                                        break;
                                                    default:
                                                        handleBalloonClick('group_1');
                                                        break;
                                                }
                                        
                                            }
                                        
                                            // Close and destroy the modal after five seconds
                                            setTimeout(function () {
                                                handleBalloonClicked('1');

                                                // Close and destroy the modal
                                                $modal.dialog('close');
                                            }, 10000);
                                        }
                                        
                                        
                                        await new Promise(resolve => setTimeout(resolve, delay));
                                        
                                        // Decrease the countdown by the update interval
                                        count -= updateInterval;

                                        // Ensure the countdown doesn't go below the minimum value
                                        if (count < minCountdown) {
                                            count = minCountdown;
                                        }

                                        // Update the text with the remaining countdown time
                                        chooseballoontext.setText('Choose balloon in ' + count + 's');
                                        if (count === 0) {
                                            break;
                                        }
                                    }
                                chooseballoontext.destroy();

                                game_id = data.game_id
                                

                                    
                                crashInstructionProcessed = false;
                                cashoutclicked = false;
                                start = true;
                               
                                startgame_official();
                               
                                
                               
                                
                            
                               
                                
                            
                        
                            
                            
                        }
                       
                    }
                    async function startgame_official(){
                        if(start_with_balloon){

                            start_with_balloon = false
                        if(window.roomName){
                            roomName = window.roomName;
                            console.log(roomName);
                            
                       

                        }
                        else{
                            window.roomName = 'group_1';
                            roomName = 'group_1';

                        }
                        groupSocket = new WebSocket(
                                'ws://'
                                + window.location.host
                                + '/ws/real_time_updates/'
                                + roomName
                                + '/'
                            );
                            console.log("connected to room");
                            
                            groupSocket.onmessage = async function (e) {
                                
                                    const data = JSON.parse(e.data);
                                    console.log(data)
                                    
                                   
                                     
                                    if (data.type === "crash_instruction") {
                                        // Handle crash instruction, e.g., trigger the crash action in the game
                                        console.log(data)
                                        groupSocket.close();
                                        
                                        const crashpoint = data.crash
                                        if (backg) {
                                            // Destroy the existing background image
                                            backg.destroy();
                                        }
                                        if (balloonsTween) {
                                            balloonsTween.stop(); // Stop the balloon animation
                                            balloonsTween = null; // Clear the tween reference
                                        }
                                        
                                        // Clear any balloons that might still be visible
                                        if (balloons) {
                                            balloons.clear(true, true);
                                        }
                                        if (animationTimer) {
                                            animationTimer.remove(); // Remove the timer
                                            animationTimer = null; // Clear the timer reference
                                        }
                                        if (pump){
                                            pump.destroy();
                                        }
                                        
                                        
                                        
                                    
                                        // Create a new background image with the new texture
                                        poppedbackground = scene.add.image(400, 300, 'popped');
                                        switch (window.roomName) {
                                            case 'group_1':
                                                // No tint (default color)
                                                break;
                                            case 'group_2':
                                                poppedbackground.setTint(0xff0000); // Red tint
                                                break;
                                            case 'group_3':
                                                poppedbackground.setTint(0x00ff00); // Green tint
                                                break;
                                            case 'group_4':
                                                poppedbackground.setTint(0x800080); // White tint
                                                break;
                                            default:
                                                console.log('Invalid group name: ' + roomName);
                                                poppedbackground.setTint(0x0000ff);
                                               
                                                break;
                                        }
                                        
                                        // isCrashTriggered = true;
                                        CountingComplete(crashpoint);
                                        console.log('back to here');
                                        if (typeof globalBetAmount !== 'undefined') {
                                            globalBetAmount = 0;
                                        }
                                        
                                        betButton.disabled = false;
                                        betButton.textContent = 'BET'
            
                                        console.log('bet_amount reset');
                                        start_initial = true;
                                        start = true;
                                        window.allowballoonchange = false
            
                                        crashInstructionProcessed = true;
                                        start_with_balloon = true
                                        
            
                                    }
            
                                           
                                            
                                        
                                    
                                        
                                        
                                    
                                    else if (data.type == "count_initial"){
                                        if (start_initial){
                                            window.allowballoonchange = false
                                            start_initial = false;
                                            if (poppedbackground) {
                                                // Destroy the existing background image
                                                poppedbackground.destroy();
                                            }
                                           
                
                                            backg = scene.add.image(400, 300, 'bg').setPipeline('Light2D');
                                            
                                            
                                            
                                        }
                                        
                                        if (countdownText) {
                                            countdownText.destroy();
                                        }
                                        
                                       
                                        if (crashText) {
                                            crashText.destroy();
                                        }
                                        countAndDisplayInitial(data.count);
            
            
                                    }
                                    
                                    
                                    else if (data.type == "count_update"){
                                        if (start){
                                            start = false;
                                            
                                            
                                            startgame(scene);
                                        }
                                        if (countdownText) {
                                            countdownText.destroy();
                                        }
                                        if (bet_allowed_text) {
                                            bet_allowed_text.destroy();
                                        }
                                        countAndDisplay();
            
            
                                    }
                                    
                                }
                        

                    }
                }
                    async function countAndDisplayInitial(count){
                       
                        if(bet_allowed_text){
                            
                            bet_allowed_text.destroy();
                               
                        }
                        if (counterText) {
                            counterText.destroy();
                        }
                        countdownText = scene.add.dynamicBitmapText(400, 400, 'desyrel', '').setOrigin(0.5, 0);
                        bet_allowed_text = scene.add.dynamicBitmapText(400, 200, 'desyrel', '').setOrigin(0.5, 0);
                        countdownText.setText(`Game starts in ${count}`);
                       
                        if(count>5){
                            
                            bet_allowed_text.setText('Place your bet');
                               
                        }
                        else {
                            if(bet_allowed_text){
                            
                                bet_allowed_text.destroy();
                                   
                            }
                        }

                        
                    
                        
                        
                        }


                    
                    async function startgame(wsSocket){
                        console.log('startgame called')
                        pump = scene.add.image(650, 450, 'pumpUp');
                        Line = new Phaser.Geom.Line(centerX-4, centerY-2, 638, 572);
                        graphics.strokeLineShape(Line);
                        // graphics.strokeLineShape(verticalLine);
                
                        // Start the animation
                        
                        
                        
                       
                
                        balloons = scene.add.group({ key: 'balloon', repeat: 50 });
                        // Function to change the tint color of balloons
                        function changeBalloonColor(balloon, roomName) {
                            switch (roomName) {
                                case 'group_1':
                                    // No tint (default color)
                                    break;
                                case 'group_2':
                                    balloon.setTint(0xff0000); // Red tint
                                    break;
                                case 'group_3':
                                    balloon.setTint(0x00ff00); // Green tint
                                    break;
                                case 'group_4':
                                    balloon.setTint(0x800080); // White tint
                                    break;
                                default:
                                    console.log('Invalid group name: ' + roomName);
                                    balloon.setTint(0x0000ff);
                                    // You may want to set a default tint here or clear the tint
                                    break;
                            }
                        }

                        // Iterate through each balloon in the group and change its color based on roomName
                        
                
                        balloons.getChildren().forEach((balloon) => {
                            changeBalloonColor(balloon, window.roomName);
                            balloon.setOrigin(0.5, 1); // Set the anchor point to the bottom center
                            balloon.setScale(0.1);
                            balloon.x = centerX; // Set the initial x position to the center
                            balloon.y = centerY+10; // Set the initial y position to the bottom
                        });
                
                        
                    
                            if (crashText) {
                                crashText.destroy();
                            }
                            
                            const cashoutButton = document.getElementById('cashout-button');
                            cashoutButton.disabled= false;
                           
                            if (countdownText) {
                                countdownText.destroy();
                            }
                            await cashout()
                            // scene.add.sprite(400, 300, 'background').play('explodeAnimation');
                            function animateImages() {
                                // Switch between 'pumpUp' and 'pumpDown'
                                currentImage = currentImage === 'pumpUp' ? 'pumpDown' : 'pumpUp';

                                // Display the current image
                                pump.setTexture(currentImage);

                                // Set a timer to call this function again after the delay
                                animationTimer = scene.time.delayedCall(delay, animateImages, [], scene);
                            }

                            animateImages.call(scene);
                             // Create a promise for each animation
                             const balloonsAnimationPromise = animateBalloons();
                             const lightsAnimationPromise = animateLights();
 
                             // Wait for both animations to complete before continuing
                             await Promise.all([balloonsAnimationPromise, lightsAnimationPromise]);

                        }

                        async function animateBalloons() {
                            const duration = 500000; // Set the desired animation duration in milliseconds
                            
                            // Your balloon animation code here...
                            balloonsTween = scene.tweens.add({
                                targets: balloons.getChildren(),
                                scaleX: 2,
                                scaleY: 2,
                                radius: 228,
                                ease: 'Quintic.easeOut',
                                duration: duration, // Use the specified duration
                                yoyo: true,
                                repeat: -1,
                                onUpdate: function () {
                                    // Update the x and y positions based on the new scale
                                    balloons.getChildren().forEach((balloon) => {
                                        balloon.x = centerX;
                                        balloon.y = centerY;
                                    });
                                },
                                onComplete: function () {
                                    // Resolve the promise when the animation is done
                                    resolve();
                                }
                            });
                        
                            return new Promise((resolve) => {});
                        }
                        
                        async function animateLights() {
                            const duration = 5000; // Set the desired animation duration in milliseconds
                            
                            // Your light animation code here...
                            scene.lights.enable().setAmbientColor(0x555555);
                        
                            const hsv = Phaser.Display.Color.HSVColorWheel();
                        
                            const radius = 80;
                            const intensity = 6;
                            let x = radius;
                            let y = 0;
                        
                            //  To change the total number of lights see the Game Config object
                            const maxLights = 20;
                        
                            //  Create a bunch of lights
                            for (let i = 0; i < maxLights; i++) {
                                const color = hsv[i * 10].color;
                        
                                light = scene.lights.addLight(x, y, radius, color, intensity);
                        
                                lightsTween = scene.tweens.add({
                                    targets: light,
                                    y: 600,
                                    yoyo: true,
                                    repeat: -1,
                                    ease: 'Sine.easeInOut',
                                    duration: duration, // Use the specified duration
                                    delay: i * 100,
                                    onComplete: function () {
                                        // Resolve the promise when the animation is done
                                        resolve();
                                    }
                                });
                        
                                x += radius * 2;
                        
                                if (x > 800) {
                                    x = radius;
                                    y += radius;
                                }
                            }
                        
                            return new Promise((resolve) => {});
                        }
                        
                   
                    async function countAndDisplayOngoing(multiplier) {
                        console.log('countAndDisplay Ongoing called')
                        if (counterText) {
                            counterText.destroy();
                        }
                       
                        const delay = 100;  // Delay in milliseconds
                        const updateInterval = 0.01;
                        const crashPoint = 1000000; // Adjust this value as needed
                        counterText = scene.add.dynamicBitmapText(400, 200, 'desyrel').setOrigin(0.5, 0);
                        bet_allowed_text = scene.add.dynamicBitmapText(400, 300, 'desyrel', '').setOrigin(0.5, 0);
                        bet_allowed_text.setText(' Ongoing game,\n Wait for new game');
                        
                            let count = multiplier;
                            while (count <= crashPoint) {
                                await new Promise(resolve => setTimeout(resolve, delay));
                                count += updateInterval;
                                const counted = Math.round(count * 100) / 100;
                                 // Assuming you have a context with 'self' available
                                counterText.setText('x' + counted);
                                 
                            }
                          
                        
                 
                        
                        
                        
                        
                            
                        
                        
                    
                    }
                    async function countAndDisplay() {
                        // Destroy the existing counterText if it exists
                        if (counterText) {
                            counterText.destroy();
                        }
                        if(bet_allowed_text){
                            
                            bet_allowed_text.destroy();
                               
                        }
                        const delay = 50;  // Delay in milliseconds
                        const updateInterval = 0.01;
                        const crashPoint = 1000000; // Adjust this value as needed
                        counterText = scene.add.dynamicBitmapText(400, 200, 'desyrel').setOrigin(0.5, 0);
                        
                        
                            let count = 1;
                            while (count <= crashPoint) {
                                await new Promise(resolve => setTimeout(resolve, delay));
                                count += updateInterval;
                                const counted = Math.round(count * 100) / 100;
                                 // Assuming you have a context with 'self' available
                                counterText.setText('x' + counted);
                                await updateCashoutButtonText(counterText); 
                            }
                          
                        
                        
                        
                            
                        
                        
                    }
                        
                    async function cashout(){
                        console.log('cashout called')
                        // Add a click event listener to the cashoutButton
                        const cashoutButton = document.getElementById('cashout-button');
                        
                        cashoutButton.addEventListener('click', function() {
                            if(!cashoutclicked){
                            cashoutclicked=true;
                            console.log('cashout clicked and value set to true');
                            
                            const cashOutValue = parseFloat(counterText.text.substring(1)); 
                            console.log('cashed_out at: ', cashOutValue);// Extract and parse the value
                            const betForm = document.getElementById("bet-form");
                            // Send the cashOutValue to the server using an API call
                           
                            const formdata = {'type':'cashout_validate', 'multiplier':cashOutValue, 'game_id':game_id}

                            
                            const data = JSON.stringify(formdata)
                            console.log(data)
                            groupSocket.send(data)

                           
                    }});
                    
                    }

                    async function updateCashoutButtonText(counterText) {
                        let bet_amount = 0;
                    
                        if (typeof globalBetAmount !== 'undefined') {
                            bet_amount = globalBetAmount;
                        }
                    
                        const cashoutButton = document.getElementById('cashout-button');
                        const counterValue = parseFloat(counterText.text.substring(1)); // Assuming counterText contains something like "$1.23"

                        const cashoutAmount = Math.floor(bet_amount * counterValue);

                        cashoutButton.textContent = `CASHOUT (${cashoutAmount})`;
                    }
                    
                        
                    function CountingComplete( crashpoint) {
                        
                        
                                clearTimeout(countAndDisplayTimer);
                                if (counterText) {
                                    counterText.destroy();
                                }
                               
                                
                                
                               
                                console.log('its the crashtexts font', crashpoint);
                                crashText = scene.add.dynamicBitmapText(400, 200, 'desyrel').setOrigin(0.5, 0);
                                crashText.setText('Popped at x' + crashpoint);
                                
                                // Schedule the text to be cleared after 5 minutes
                                setTimeout(() => {
                                    crashText.destroy();
                                }, 5000); // 5 minutes in milliseconds                          
     

                }
                    function drawgraph(scene, wsSocket){
                        
                                               
                
                       
                        
                    
                                
                      
                        
                      
                      
                        
                        
                 



                        
            
                    }
                   
                   
                         
                       
                    
        } catch (error) {
            console.error('Error fetching new crash point:', error);
        }
        
}
main(scene);

    }
}