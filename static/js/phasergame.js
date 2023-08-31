

class Example extends Phaser.Scene 
    
{
   

    preload ()
    {
        this.load.setBaseURL('https://labs.phaser.io')

        this.load.image('bg', 'assets/tweens/background.jpg');
        
        this.load.bitmapFont('desyrel', 'assets/fonts/bitmap/desyrel.png', 'assets/fonts/bitmap/desyrel.xml');
    }

   async create ()
    {
        
    
        console.log('create called');
        const scene = this;

        const graphics = scene.add.graphics({ lineStyle: { width: 2, color: 0x00aa00 } });
        const horizontalLine = new Phaser.Geom.Line(100, 500, 700, 500);
        const verticalLine = new Phaser.Geom.Line(100, 500, 100, 100);
        
        const counterLimit = 3.0;
       
        async function main(scene) {
            try {
                
                const wsSocket = new WebSocket("wss://" + window.location.host + "/ws/realtime/");
                let isCrashTriggered = false; 
                let tween;
                graphics.strokeLineShape(horizontalLine);
                graphics.strokeLineShape(verticalLine); 

                graphics.lineStyle(2, 0xaa0000);

                scene.add.text(400, 28, '').setColor('#00ff00').setFontSize(32).setShadow(2, 2).setOrigin(0.5, 0);
                

                const types = [ 'sinu.in' ];
                let type = 0;
                // let tween;

                

                const graph = scene.add.graphics();
                graphics.lineGradientStyle(128, 0xff0000, 0xff0000, 0x0000ff, 0x0000ff, 1);

                const rect = scene.add.rectangle(100, 400, 2, 2, 0x00ff00);
                const rt = scene.add.renderTexture(400, 300, 800, 600);
                // const counterText = scene.add.dynamicBitmapText(400, 200, 'desyrel', '0.00').setOrigin(0.5, 0);
                const crashText = scene.add.dynamicBitmapText(400, 200, 'desyrel', '0.00').setOrigin(0.5, 0);
                
                let crashInstructionProcessed = false;
                let countAndDisplayTimer;   
                let continueCounting = true;
                const delayTime = 10;    
                let counterText;
                let countdownText;
                let cashoutclicked = false;
               
                
                
                
                
                let start = true;
                const betButton = document.getElementById("bet-button");
                let game_id;
               
                
                rect.setPosition(100, 500);
                wsSocket.onmessage = async function (e) {
                        const data = JSON.parse(e.data);
                        
                        if (data.type == "ongoing_synchronizer") {
                            // Use the current multiplier to render the ongoing graph
                            const currentMultiplier = data.currentMultiplier; // Assuming the currentMultiplier is provided in the data
                            // Use currentMultiplier to render the ongoing graph
                            
                            countAndDisplay(currentMultiplier);
                            if (counterText) {
                                counterText.destroy();
                            }
                            if (crashText) {
                                crashText.destroy();
                            }
                            console.log(data)
                        }
                         
                        else if (data.type === "crash_instruction") {
                            // Handle crash instruction, e.g., trigger the crash action in the game
                            console.log(data)
                            const crashpoint = data.crash
                            // isCrashTriggered = true;
                            CountingComplete(tween,graph, rect, rt, crashpoint);
                            console.log('back to here');
                            if (typeof globalBetAmount !== 'undefined') {
                                globalBetAmount = 0;
                            }
                            
                            betButton.disabled = false;
                            betButton.textContent = 'BET'

                            console.log('bet_amount reset');
                            
                            

                            crashInstructionProcessed = true;

                        } else if (data.type == "start_synchronizer") {
                            // Start the synchronizer countdown
                            
                                if (tween) {
                                    tween.stop();
                                }
                                
                                crashInstructionProcessed = false;
                                cashoutclicked = false;
                                game_id = data.game_id
                                console.log(game_id);
                                console.log(data);
                                startgame(wsSocket);
                                // Assuming the count is provided in the data
                            
                        
                            
                            
                        }
                        else if (data.type == "count_initial"){
                            if (countdownText) {
                                countdownText.destroy();
                            }
                            if (tween) {
                                tween.stop();
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
                            if (countdownText) {
                                countdownText.destroy();
                            }
                            countAndDisplay(data.count);


                        }
                        else if (data.type == "heartbeat"){
                            console.log('heartbeat')
                            wsSocket.send(JSON.stringify({ type: 'heartbeat_response' }));


                        }
                    }
                    async function countAndDisplayInitial(count){
                        countdownText = scene.add.dynamicBitmapText(400, 300, 'desyrel', '0.00').setOrigin(0.5, 0);
                        countdownText.setText(`Game starts in ${count}`);

                    }
                    async function startgame(wsSocket){
                        console.log('startgame called')
                            if (crashText) {
                                crashText.destroy();
                            }
                            const cashoutButton = document.getElementById('cashout-button');
                            cashoutButton.disabled= false;
                            // countdownText = scene.add.dynamicBitmapText(400, 300, 'desyrel', '0.00').setOrigin(0.5, 0);
                            // console.log('countdownText created')
                            // for (let countValue = countdown; countValue >= 0; countValue--) {
                                
                    
                            //     countdownText.setText(`Game starts in ${countValue}`);
                            //     await new Promise(resolve => setTimeout(resolve, 1000));
                            // }
                            if (countdownText) {
                                countdownText.destroy();
                            }
                            await cashout()
                        
                            drawgraph(scene, wsSocket);


                    }
                   
                    
                    async function countAndDisplay(count) {
                        // Destroy the existing counterText if it exists
                        if (counterText) {
                            counterText.destroy();
                        }
                        
                        // Create a new counterText
                        counterText = scene.add.dynamicBitmapText(400, 200, 'desyrel').setOrigin(0.5, 0);
                    
                        // Set the text of the counterText
                        counterText.setText('x' + count);
                    
                        
                        
                        
                        
                            
                        await updateCashoutButtonText(counterText); 
                        
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
                            const formData = new FormData();
                            formData.append('multiplier', cashOutValue);
                            formData.append('game_id', game_id);

                            const csrfToken = betForm.querySelector('[name=csrfmiddlewaretoken]').value;
                                                
                            fetch('/cashout/', {
                                method: 'POST',
                                headers: {
                                    'X-CSRFToken': csrfToken // Make sure to define csrfToken
                                },
                                body: formData
                            })
                            .then(response => response.json())
                            .then(data => {
                                console.log('data sent', data);
                                cashoutButton.textContent = 'CASH OUT';
                                cashoutButton.disabled = true;
                                
                                // Update the page content using the data received from the server
                                // For example, update the user's balance or display a success message
                            })
                            .catch(error => {
                                console.error('Error:', error);
                            });
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
                    
                        
                    function CountingComplete(tween, graph, rect, rt, crashpoint) {
                        
                        if (tween) {
                            tween.stop();
                        }
                                clearTimeout(countAndDisplayTimer);
                                if (counterText) {
                                    counterText.destroy();
                                }
                                graph.clear();
                                rt.clear();                                                        
                            
                                rect.setPosition(100, 500);
                                
                               
                                console.log('its the crashtexts font', crashpoint);
                                let text = scene.add.text(400, 28, 'Crashed at x' + crashpoint);
                                text.setColor('#00ff00').setFontSize(32).setShadow(2, 2).setOrigin(0.5, 0);
                                
                                // Schedule the text to be cleared after 5 minutes
                                setTimeout(() => {
                                    text.destroy();
                                }, 2000); // 5 minutes in milliseconds                          
     

                }
                    function drawgraph(scene, wsSocket){
                        
                        const newCrashPoint = 200;
                        console.log("we're here", newCrashPoint);
                        
                       
                        
                        console.log("I think we crash here");
                        // Update crash point value and re-render
                        const crashPointValue = newCrashPoint;
            
                
                        let stopValue = crashPointValue;
                        

                        if (stopValue==1){
                            crashText.setText('Crashed at x' + stopValue.toFixed(2));
                            setTimeout(() => {
                                scene.scene.restart();;
                            }, 5000);
                            
                        }
                
                
                       
                        // const cashOutButton = scene.add.text(400, 550, 'Cash Out', {
                        //     color: '#ffffff',
                        //     fontSize: 24,
                        //     backgroundColor: '#FF0000',
                        //     padding: {
                        //         x: 10,
                        //         y: 5,
                        //     },
                        // }).setOrigin(0.5).setInteractive();
                        
                            // Send a request to the server to cash out
                            
                        // cashOutButton.on('pointerdown', () => {
                        //     // Send a request to the server to cash out
                        //     const cashOutValue = parseFloat(counterText.text.substring(1)); // Extract and parse the value
                        //     // Send the cashOutValue to the server using an API call, WebSocket, or any suitable method
                        //     // Example using fetch:
                        //     console.log(cashOutValue)
                            
                       
                        // });
                        
                        
                    
                                
                      
                        
                      
                      
                        function CountingComplete () {
                            tween.stop();
                                    graph.clear();
                                    rt.clear();
                                    graph.clear();
                                    
                                
                                    rect.setPosition(100, 500);
                                    counterText.destroy();
                                    crashText.setText('Crashed at x' + stopValue.toFixed(2));
                                    // setTimeout(() => {
                                    //     fetchNewCrashPointAndRender(scene);
                                    // }, 5000);
                        }
                        
                        
                        
                        
                        function limits() {
                            
                            console.log('function limits called');
                            console.log('stopValue',stopValue);
                            
                            let limitx = 600 - ((stopValue - 1) / 2) * 600;
                            let limity = 400 - ((stopValue - 1) / 2) * 400;
                            let progres =((stopValue - 1) / 2) * 700;
                            let durationi = ((stopValue - 1) / 3) * 30000;
                            console.log('limitx', limitx);
                            
                            // Ensure limity is not negative
                            if (durationi > 30000) {
                                durationi = 30000
                            }
                            if (limity < 0) {
                                limity = 0;
                            }
                        
                            // Ensure limitx is not negative
                            if (limitx < 0) {
                                limitx = 0;
                            }
                            
                            return { limitx, limity, progres, durationi};
                        }
                 

                        const graphEase  = () => {
                            console.log('graphEase called');
                            
                            crashText.destroy()
                           
                            const { limitx, limity, progres, durationi } = limits();
                            if (tween) {
                                tween.stop();
                            }

                            rt.clear();
                            graph.clear();
                            graph.lineStyle(1, 0x00ff00);
                            graphics.lineGradientStyle(6, 0xffff00, 0xff00ff, 0xff0000, 0x0000ff, 1);
                            graph.beginPath();

                            rect.setPosition(100, 500);

                            tween = scene.tweens.add({
                                targets: rect,
                                x: { value: 700 - limitx, ease: 'expo' },
                                y: { value: 100 + limity, ease: types[type] },
                                duration: durationi,
                                onUpdate: (tween, target, key) => {
                                    if (key === 'x') {
                                        rt.draw(rect);
                                        graph.lineTo(rect.x, rect.y);
                                        
                                        // Update the counter text based on tween progress
                                        const progress1 = tween.getValue();
                                        const progress2 = progress1-100;
                                        const progress = progress1;
                                        // console.log('progress',progress);
                                        // const counterValue = ((progress / 700) * 3)+1;
                                        // Calculate counter value based on stopValue
                                        // counterText.setText('x'+ counterValue.toFixed(2));
                                        
                                        if (progress2 >= progres) { // Stop the tween when the progress reaches half (350) of the total duration
                                            tween.stop();
                                            graph.clear();
                                            rt.clear();
                                            graph.clear();
                                            
                                        
                                            rect.setPosition(100, 500);
                                            counterText.destroy();
                                            // crashText.setText('Crashed at x' + counterValue.toFixed(2));
                                        }
                        
                                    }
                                },
                            
                                onComplete: () => {
                                    graph.stroke();
                                    tween.stop();
                                    
                                
                                }
                            });
                        }


                        graphEase();
            
                    }
                   
                    // function CountingComplete(tween,graph, rect, rt, counterText, crashText, crashpoint) {
                    //     WebFont.load({
                    //         google: {
                    //             families: ['Droid Sans']
                    //           },
                    //         active: function () {
                    //             if (tween) {
                    //                 tween.stop();
                    //             }
                    //                     graph.clear();
                    //                     rt.clear();
                                        
                                        
                                    
                    //                     rect.setPosition(100, 500);
                    //                     counterText.destroy();
                    //                     console.log('its the crashtexts font');
                    //                     crashText.setText('Crashed at x' + crashpoint.toFixed(2));
                    //                     scene.scene.restart();
                                       
                            
                    //           // Your code when fonts are loaded
                    //         },
                    //         inactive: function () {
                    //             console.log('inactive');
                    //           // Your code when fonts failed to load
                    //         }
                    //       });

                    //     }
                          
                         
                       
                    
        } catch (error) {
            console.error('Error fetching new crash point:', error);
        }
        
}
main(scene);

    }
}
