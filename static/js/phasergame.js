

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
                
                const wsSocket = new WebSocket("wss://" + window.location.host + "/ws/realtime/");
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

                wsSocket.onmessage = async function (e) {
                    if(loading_game){
                        loading_game.destroy();}
                        const data = JSON.parse(e.data);
                        
                        if (data.type == "ongoing_synchronizer") {
                            // Use the current multiplier to render the ongoing graph
                            const currentMultiplier = data.cached_multiplier; // Assuming the currentMultiplier is provided in the data
                            // Use currentMultiplier to render the ongoing graph
                            console.log('ongoing synchronizer');
                            countAndDisplayOngoing(currentMultiplier);
                            // if (counterText) {
                            //     counterText.destroy();
                            // }
                            // if (crashText) {
                            //     crashText.destroy();
                           // }
                            console.log(data)
                        }
                         
                        else if (data.type === "crash_instruction") {
                            // Handle crash instruction, e.g., trigger the crash action in the game
                            console.log(data)
                            
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
                            
                            // isCrashTriggered = true;
                            CountingComplete(crashpoint);
                            console.log('back to here');
                            if (typeof globalBetAmount !== 'undefined') {
                                globalBetAmount = 0;
                            }
                            
                            betButton.disabled = false;
                            betButton.textContent = 'BET'

                            console.log('bet_amount reset');
                            start_initial = true
                            

                            crashInstructionProcessed = true;

                        } else if (data.type == "start_synchronizer") {
                            // Start the synchronizer countdown
                               
                                if (counterText) {
                                    counterText.destroy();
                                }
                                if (bet_allowed_text) {
                                    bet_allowed_text.destroy();
                                }
                                    
                                crashInstructionProcessed = false;
                                cashoutclicked = false;
                                start = true;
                                game_id = data.game_id
                                console.log(game_id);
                                console.log(data);
                                
                               
                                
                            
                        
                            
                            
                        }
                        else if (data.type == "count_initial"){
                            if (start_initial){
                                start_initial = false;
                                if (poppedbackground) {
                                    // Destroy the existing background image
                                    poppedbackground.destroy();
                                }
                                if (backg) {
                                    // Destroy the existing background image
                                    backg.destroy();
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
                        else if (data.type == "heartbeat"){
                            console.log('heartbeat')
                            wsSocket.send(JSON.stringify({ type: 'heartbeat_response' }));


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
                        else if (data.type == "heartbeat"){
                            console.log('heartbeat')
                            wsSocket.send(JSON.stringify({ type: 'heartbeat_response' }));


                        }
                    }
                    async function countAndDisplayInitial(count){
                        if(bet_allowed_text){
                            
                            bet_allowed_text.destroy();
                               
                        }
                        if (counterText) {
                            counterText.destroy();
                        }
                        countdownText = scene.add.dynamicBitmapText(400, 300, 'desyrel', '').setOrigin(0.5, 0);
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
                
                        balloons.getChildren().forEach((balloon) => {
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
                        const delay = 100;  // Delay in milliseconds
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
                            wsSocket.send(data)

                           
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
                                }, 2000); // 5 minutes in milliseconds                          
     

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