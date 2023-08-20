
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
                // Fetch new crash point from the server
                const response = await fetch('/get-new-crash-point'); // Use the correct URL path
                console.log(response);
                
                const responseData = await response.json();
                console.log('Raw response data:', responseData);
                
                if ('crash_point' in responseData) {
                    const newCrashPoint = responseData.crash_point;
                    console.log("we're here", newCrashPoint);
                    
                    // Display countdown and wait for 5 seconds
                    const countdownText = scene.add.dynamicBitmapText(400, 300, 'desyrel', '0.00').setOrigin(0.5, 0);
                    
                                for (let count = 4; count >= 0; count--) {
                                    countdownText.setText(`Game starts in ${count}`);
                                    await new Promise(resolve => setTimeout(resolve, 1000));
                                }
                    
                    
                    console.log("I think we crash here");
                    // Update crash point value and re-render
                    const crashPointValue = newCrashPoint;
        
                    // Continue with your code that uses the crashPointValue
                    // ...
                   
               
                    let stopValue = crashPointValue;
                    const crashText = scene.add.text(400, 200, '', {
                        color: '#00ff00',
                        fontSize: 32,
                        shadow: { offsetX: 2, offsetY: 2 }
                    }).setOrigin(0.5, 0);

                    if (stopValue==1){
                        crashText.setText('Crashed at x' + stopValue.toFixed(2));
                        setTimeout(() => {
                            scene.scene.restart();;
                        }, 5000);
                        
                    }
            
            
                    // const counterText = scene.add.bitmapText(600, 550, 'fontKey', '0.00', 24);


                    graphics.strokeLineShape(horizontalLine);
                    graphics.strokeLineShape(verticalLine); 

                    graphics.lineStyle(2, 0xaa0000);

                    scene.add.text(400, 28, '').setColor('#00ff00').setFontSize(32).setShadow(2, 2).setOrigin(0.5, 0);
                    

                    const types = [ 'quad.in' ];
                    let type = 0;
                    let tween;

                    

                    const graph = scene.add.graphics();
                    graphics.lineGradientStyle(128, 0xff0000, 0xff0000, 0x0000ff, 0x0000ff, 1);

                    const rect = scene.add.rectangle(100, 400, 2, 2, 0x00ff00);
                    const rt = scene.add.renderTexture(400, 300, 800, 600);
                    const counterText = scene.add.dynamicBitmapText(400, 200, 'desyrel', '0.00').setOrigin(0.5, 0);
                    // Display Cash Out button
                    const cashOutButton = scene.add.text(400, 550, 'Cash Out', {
                        color: '#ffffff',
                        fontSize: 24,
                        backgroundColor: '#0000FF',
                        padding: {
                            x: 10,
                            y: 5,
                        },
                    }).setOrigin(0.5).setInteractive();
                    cashOutButton.on('pointerdown', () => {
                        // Send a request to the server to cash out
                        const cashOutValue = parseFloat(counterText.text.substring(1)); // Extract and parse the value
                        // Send the cashOutValue to the server using an API call, WebSocket, or any suitable method
                        // Example using fetch:
                        console.log(cashOutValue)
                    // fetch('/cash-out/', {
                    //         method: 'POST',
                    //         headers: {
                    //             'Content-Type': 'application/json',
                    //             // Include any necessary authentication headers
                    //         },
                    //         body: JSON.stringify({ cashOutValue }),
                    //     })
                    //     .then(response => response.json())
                    //     .then(data => {
                    //         // Handle the server response, e.g., display a confirmation message
                    //         console.log(data.message);
                    //     })
                    //     .catch(error => {
                    //         console.error('Error:', error);
                    //     });
                    });
                    
                    
                
                    const delayTime = 0.69;

                    async function fetchNewCrashPointAndRender(scene) {
                        try {
                            
                    
                                
                                scene.scene.restart();
                          
                        } catch (error) {
                            console.error('Error fetching rerendering:', error);
                        }
                    }
                    
                    
                    
                    
                    
                    
                    
                    
                    function formatTime(milliseconds) {
                        const seconds = (1+Math.floor(milliseconds / 1000));
                        const scaledMilliseconds = Math.floor((milliseconds % 1000) / 10); // Scale to 0-99 range
                        return `${seconds}.${scaledMilliseconds}`;
                    }
                    
                    function countAndDisplay(stopValueInSeconds, delayTime, onComplete) {
                        const stopValueInMilliseconds = Math.floor((stopValueInSeconds-1) * 1000);
                        console.log('stopvalueinms',stopValueInMilliseconds);
                        let currentValue = 0;
                    
                        function update() {
                            currentValue += delayTime;
                            const displayValue = formatTime(currentValue)   ;
                            counterText.setText('x'+ displayValue);
                    
                            if (currentValue <= stopValueInMilliseconds) {
                                setTimeout(update, delayTime);
                            } else {
                                CountingComplete();
                            }
                        }
                    
                        update();
                    }
                    function CountingComplete () {
                        tween.stop();
                                graph.clear();
                                rt.clear();
                                graph.clear();
                                
                            
                                rect.setPosition(100, 500);
                                counterText.destroy();
                                crashText.setText('Crashed at x' + stopValue.toFixed(2));
                                setTimeout(() => {
                                    fetchNewCrashPointAndRender(scene);
                                }, 5000);
                    }
                    
                    
                    
                    
                    function limits() {
                        
                        console.log('function limits called');
                        console.log('stopValue',stopValue);
                        countAndDisplay(stopValue, delayTime);
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
                    
                    // ...
                    
                    
                    

                    const graphEase  = () => {
                        console.log('graphEase called');
                        countdownText.destroy();
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
                            x: { value: 700 - limitx, ease: 'linear' },
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
                                    const counterValue = ((progress / 700) * 3)+1;
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
            } else {
                console.error('Crash point not found in response data');
            }
        } catch (error) {
            console.error('Error fetching new crash point:', error);
        }
        
}
main(scene);

    }
}
