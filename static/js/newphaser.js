
class Example extends Phaser.Scene {
	preload() {
		this.load.image('balloon', balloon);

		this.load.image('bg', space);
		this.load.image('pumpUp', pumpup);
		this.load.image('pumpDown', pumpdown);

		this.load.image('popped', popped);

		this.load.bitmapFont('desyrel', desyrelpng, desyrelxml);
	}

	async create() {
		const scene = this;
		let backg = scene.add.image(400, 300, 'bg');
		backg.setScale(2.7, 3.5);

		const loading_game = scene.add.text(400, 28, 'Game loading....').setColor('#00ff00').setFontSize(32).setShadow(2, 2).setOrigin(0.5, 0);

		let currentImage = 'pumpUp'; // Start with 'pump up'
		let balloonsTween = null;
		let lightsTween = null;
		const graph = scene.add.graphics();
		const delay = 200; // Delay in milliseconds (0.1 seconds)

		const centerX = 400;
		const centerY = 500;

		// Create a strong point line
		const graphics = scene.add.graphics({ lineStyle: { width: 6, color: 0x0000ff } });

		// Const counterText = scene.add.dynamicBitmapText(400, 200, 'desyrel', '0.00').setOrigin(0.5, 0);

		let counterText;
		let countdownText;
		let crashText;
		let bet_allowed_text;
		let cashoutclicked = false;

		let start = true;
		const betButton = document.getElementById('bet-button');
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
		const isCrashTriggered = false;
		let selectedBalloon = null;
		let balloons_to_show = [];
		let balloonsalreadychosen = false;
        let stopCounting = false;
        let isAnimationCancelled = false;
        
		main(scene);

		
        
       

		async function main(scene) {
			try {
				// await animateLights();

				// async function animateLights() {
				// 	console.log('lights called')
				// 	const duration = 5000;
				// 	scene.lights.enable().setAmbientColor(0x555555);
		
				// 	const hsv = Phaser.Display.Color.HSVColorWheel();
		
				// 	const radius = 80;
				// 	const intensity = 6;
				// 	let x = radius;
				// 	let y = 0;
		
				// 	//  To change the total number of lights see the Game Config object
				// 	const maxLights = 3;
		
				// 	//  Create a bunch of lights
				// 	for (let i = 0; i < maxLights; i++) {
				// 		const { color } = hsv[i * 10];
		
				// 		light = scene.lights.addLight(x, y, radius, color, intensity);
		
				// 		lightsTween = scene.tweens.add({
				// 			targets: light,
				// 			y: 600,
				// 			yoyo: true,
				// 			repeat: -1,
				// 			ease: 'Sine.easeInOut',
				// 			duration, // Use the specified duration
				// 			delay: i * 100,
				// 			onComplete() {
				// 				// Resolve the promise when the animation is done
				// 				resolve();
				// 			},
				// 		});
		
				// 		x += radius * 2;
		
				// 		if (x > 800) {
				// 			x = radius;
				// 			y += radius;
				// 		}
				// 	}
		
				// 	return new Promise(resolve => { });
				// }
				console.log('main called')
				const wsSocket = new WebSocket('wss://' + window.location.host + '/ws/realtime/');
				// Const wsSocket = new WebSocket('wss://'
				// + window.location.host
				// + '/ws/real_time_updates/'
				// + 'group_1'
				// + '/');

				// Scene.add.sprite(400, 300, 'background').play('explodeAnimation');

				backg = scene.add.image(400, 300, 'bg').setPipeline('Light2D');
				backg.setScale(2.7, 3.5);

				wsSocket.onmessage = async function (e) {
					if (loading_game) {
						loading_game.destroy();
					}

					const data = JSON.parse(e.data);
					console.log(data);

					if (data.type === 'ongoing_synchronizer') {
						// Use the current multiplier to render the ongoing graph
						const currentMultiplier = data.cached_multiplier; // Assuming the currentMultiplier is provided in the data
						// Use currentMultiplier to render the ongoing graph

						countAndDisplayOngoing(currentMultiplier);
					} else if (data.type === 'start_synchronizer') {
						if (groupSocket) {
							groupSocket.close();
						}
						if (chooseballoontext) {
							chooseballoontext.destroy();
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

						if (pump) {
							pump.destroy();
						}


						balloonsalreadychosen = false;
						window.allowballoonchange = true;
						showballoons = true;
						chooseballoontext = scene.add.dynamicBitmapText(400, 100, 'desyrel').setOrigin(0.5, 0);

						chooseballoontext.setText('Choose balloon.\n Game starts soon.');
					} else if (data.type === 'mid_start_synchronizer') {
						if (chooseballoontext) {
							chooseballoontext.destroy();
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

						if (pump) {
							pump.destroy();
						}

						window.allowballoonchange = true;
						showballoons = true;
						choose_balloon(data.data);
					}
					// } else if (data.type === 'game_already_started') {
					// 	bet_allowed_text = scene.add.dynamicBitmapText(400, 100, 'desyrel').setOrigin(0.5, 0);

					// 	bet_allowed_text.setText('Wait for new game');
					// }
				};
			} catch (error) {
				console.error('Error fetching new crash point:', error);
			}
		}

		
		async function choose_balloon(data) {
			// Start the synchronizer countdown

			if (crashText) {
				crashText.destroy();
			}
			if (chooseballoontext) {
				chooseballoontext.destroy();
			}
			if (crashText){
				crashText.destroy();
			}

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


			if (balloons_to_show) {
				for (var i = 0; i < balloons_to_show.length; i++) {
					balloons_to_show[i].destroy();
				}

			}

			const delay = 1000; // Delay in milliseconds
			const updateInterval = 1;
			const crashPoint = 10; // Adjust this value as needed
			// chooseballoontext = scene.add.dynamicBitmapText(400, 100, 'desyrel').setOrigin(0.5, 0);

			let balloon_to_add;

			const balloonColors = [0x54deff, 0xff0000, 0x00ff00, 0x800080]; // Blue, Red, Green, Purple

			// Define the minimum countdown value (0 seconds)
			const minCountdown = 2;
			const count = data.count;

			if (count >= minCountdown) {
				if (chooseballoontext) {
					chooseballoontext.destroy();
				}

				chooseballoontext = scene.add.dynamicBitmapText(400, 100, 'desyrel').setOrigin(0.5, 0);

				chooseballoontext.setText(`Choose balloon in ${count - 1}`);

				if (showballoons) {
					showballoons = false;

					for (var i = 0; i < 4; i++) {
						const xPosition = 150 + i * 150; // Adjust the x position as needed
						const groupName = 'group_' + (i + 1); // Create group names 'group_1', 'group_2', ...
						balloon_to_add = scene.add.image(xPosition, 300, 'balloon');
						balloon_to_add.setTint(balloonColors[i]); // Set the balloon color based on the array
						balloon_to_add.setInteractive();
						balloon_to_add.setData('group', groupName); // Store the group name as data
						balloon_to_add.setScale(0.3);

						balloon_to_add.on('pointerdown', function () {
							const group = this.getData('group');
							if (selectedBalloon !== null) {
								selectedBalloon.removeTick(); // Remove the tick from the previously selected balloon
							}

							this.addTick(); // Add a tick below the clicked balloon
							selectedBalloon = this; // Set the selected balloon
							handleBalloonClick(group); // Call the function with the group name
						});

						balloon_to_add.addTick = function () {
							// Add a tick (e.g., a line) below the balloon
							const tick = scene.add.line(0, 0, 0, 20, 0, 0, 0xffffff);
							tick.setStrokeStyle(3, 0xffffff);
							tick.x = this.x;
							tick.y = this.y + this.displayHeight / 2 + 10;
							tick.setOrigin(0, 0);
							this.tick = tick;
						};

						balloon_to_add.removeTick = function () {
							// Remove the tick from the balloon
							if (this.tick) {
								this.tick.destroy();
								this.tick = null;
							}
						};

						balloons_to_show.push(balloon_to_add);
					}
				}

				return;

				// Ensure the countdown doesn't go below the minimum value

				// Update the text with the remaining countdown time
				// chooseballoontext.setText('Choose balloon in ' + count + 's');
			}

			if (chooseballoontext) {
				chooseballoontext.destroy();
			}
			game_id = data.game_id;

			cashoutclicked = false;
			start = true;

			await startgame_official();






		}

		async function startgame_official() {
			if (!balloonsalreadychosen) {
				balloonsalreadychosen = true;
				window.allowballoonchange = true;
				betButton.disabled = false;

				start_with_balloon = false;

				if (window.roomName) {
					roomName = window.roomName;
					handleBalloonClick(roomName);
					groupSocket = new WebSocket(
						'wss://'
						+ window.location.host
						+ '/ws/real_time_updates/'
						+ roomName
						+ '/',
					);
					await continuation_of_start_game_official();
				} else {
					roomName = 'group_1';
					handleBalloonClick(roomName);
					groupSocket = new WebSocket(
						'wss://'
						+ window.location.host
						+ '/ws/real_time_updates/'
						+ roomName
						+ '/',
					);
					await continuation_of_start_game_official();
				}
			}
		}

		async function continuation_of_start_game_official() {
			window.allowballoonchange = false;
			bet_allowed_text = scene.add.dynamicBitmapText(400, 200, 'desyrel', '').setOrigin(0.5, 0);

			bet_allowed_text.setText('Place your bet');

			groupSocket.onmessage = async function (e) {
				const data = JSON.parse(e.data);

				if (data.type === 'crash_instruction') {
					// Handle crash instruction, e.g., trigger the crash action in the game
                    await stopCountingAndBalloonsFunction();
					groupSocket.close();

					const crashpoint = data.crash;
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

					if (pump) {
						pump.destroy();
					}
					
						

					// Create a new background image with the new texture
					poppedbackground = scene.add.image(400, 300, 'popped');
					poppedbackground.setScale(3.5, 3.5);
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

							poppedbackground.setTint(0x0000ff);

							break;
					}

					// IsCrashTriggered = true;
					CountingComplete(crashpoint);

					if (typeof globalBetAmount !== 'undefined') {
						globalBetAmount = 0;
					}

					betButton.disabled = false;
					betButton.textContent = 'BET';

					start_initial = true;
					start = true;
					window.allowballoonchange = false;

					start_with_balloon = true;
				} else if (data.type == 'count_initial') {
					if (start_initial) {
						window.allowballoonchange = false;
						start_initial = false;
						if (poppedbackground) {
							// Destroy the existing background image
							poppedbackground.destroy();
						}

						backg = scene.add.image(400, 300, 'bg').setPipeline('Light2D');
						backg.setScale(2.7, 3.5);
					}

					if (countdownText) {
						countdownText.destroy();
					}

					if (crashText) {
						crashText.destroy();
					}

					await countAndDisplayInitial(data.count);
				} else if (data.type == 'count_update') {
					if (start) {
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
			};


		}

		async function countAndDisplayInitial(count) {
			if (count > 20) {
				groupSocket.close();
				return;
			}

			if (bet_allowed_text) {
				bet_allowed_text.destroy();
			}

			if (counterText) {
				counterText.destroy();
			}

			countdownText = scene.add.dynamicBitmapText(400, 400, 'desyrel', '').setOrigin(0.5, 0);
			bet_allowed_text = scene.add.dynamicBitmapText(400, 200, 'desyrel', '').setOrigin(0.5, 0);
			countdownText.setText(`Game starts in ${count}`);

			if (count > 1) {
				bet_allowed_text.setText('Place your bet');
			} else if (bet_allowed_text) {
				bet_allowed_text.destroy();
			}
		}

		async function startgame(wsSocket) {
		    stopCounting = false;
		    isAnimationCancelled = false;
			pump = scene.add.image(650, 450, 'pumpUp');
			Line = new Phaser.Geom.Line(centerX - 4, centerY - 2, 638, 572);
			graphics.strokeLineShape(Line);
			// Graphics.strokeLineShape(verticalLine);

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

						balloon.setTint(0x0000ff);
						// You may want to set a default tint here or clear the tint
						break;
				}
			}

			// Iterate through each balloon in the group and change its color based on roomName

			balloons.getChildren().forEach(balloon => {
				changeBalloonColor(balloon, window.roomName);
				balloon.setOrigin(0.5, 1); // Set the anchor point to the bottom center
				balloon.setScale(0.5);
				balloon.x = centerX; // Set the initial x position to the center
				balloon.y = centerY + 10; // Set the initial y position to the bottom
			});

			if (crashText) {
				crashText.destroy();
			}

			const cashoutButton = document.getElementById('cashout-button');
			cashoutButton.disabled = false;

			if (countdownText) {
				countdownText.destroy();
			}

			await cashout();
			// Scene.add.sprite(400, 300, 'background').play('explodeAnimation');
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
			

			// Wait for both animations to complete before continuing
			await Promise.all([balloonsAnimationPromise]);
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
				duration, // Use the specified duration
				yoyo: true,
				repeat: -1,
				onUpdate() {
                // Check for cancellation within the onUpdate function
                if (isAnimationCancelled) {
                    balloonsTween.stop();
                    reject(new Error('Animation was cancelled.'));
                } else {
                    // Update the x and y positions based on the new scale
                    balloons.getChildren().forEach(balloon => {
                        balloon.x = centerX;
                        balloon.y = centerY;
                    });
                }
            },
				onComplete() {
					// Resolve the promise when the animation is done
					resolve();
				},
			});

			return new Promise(resolve => { });
		}

		

		async function countAndDisplayOngoing(multiplier) {
			if (counterText) {
				counterText.destroy();
			}

			if (bet_allowed_text) {
				bet_allowed_text.destroy();
			}

			const delay = 110; // Delay in milliseconds
			const updateInterval = 0.01;
			const crashPoint = 1000000; // Adjust this value as needed
			counterText = scene.add.dynamicBitmapText(400, 200, 'desyrel').setOrigin(0.5, 0);
			bet_allowed_text = scene.add.dynamicBitmapText(400, 300, 'desyrel', '').setOrigin(0.5, 0);
			bet_allowed_text.setText(' Ongoing game,\n Wait for new game');

			let count = multiplier;

			async function update() {
				while (count <= crashPoint) {
					await new Promise(resolve => setTimeout(resolve, delay));
					count += updateInterval;
					let counted = Math.round(count * 100) / 100;
					if (count < window.multiplier) {
						count = window.multiplier;
						counted = count.toFixed(2);
					}

					// Check if counterText is still valid before setting text
					try {
						if (!counterText) {
							throw new Error('counterText is null.');
						}

						counterText.setText('x' + counted);
					} catch (error) {
						console.error(`error is ${error.message}`);
						break;
					}

					// Schedule the next update
				}
			}

			// Start the asynchronous update loop
			update();
		}

		async function countAndDisplay() {
			// Destroy the existing counterText if it exists

			if (counterText) {
				counterText.destroy();
			}

			if (bet_allowed_text) {
				bet_allowed_text.destroy();
			}

			const delay = 110; // Delay in milliseconds
			const updateInterval = 0.01;
			const crashPoint = 1000000; // Adjust this value as needed
			counterText = scene.add.dynamicBitmapText(400, 200, 'desyrel').setOrigin(0.5, 0);

			let count = 1;
			if (window.multiplier !== undefined) {
				window.multiplier = 1;
			}

			

			async function update() {
                while (!stopCounting && count <= crashPoint) {
                    await new Promise(resolve => setTimeout(resolve, delay));
                    count += updateInterval;
                    let counted = Math.round(count * 100) / 100;
                    if (count > 1.5) {
                        if (count < window.multiplier) {
                            count = window.multiplier;
                            counted = count.toFixed(2);
                        }
                    }

                    // Check if counterText is still valid before setting text
                    try {
                        if (!counterText) {
                            throw new Error('counterText is null.');
                        }

                        counterText.setText('x' + counted);
                        await updateCashoutButtonText(counterText);
                    } catch (error) {
                        console.error(`error is ${error.message}`);
                        break;
                    }

                    // Schedule the next update
                }
            }

            // Start the asynchronous update loop
            await update(); // Wait for the update function to complete
        }

        // To stop counting, set stopCounting to true from outside the function
        function stopCountingAndBalloonsFunction() {
            stopCounting = true;
            isAnimationCancelled = true;
        }


		async function cashout() {
			// Add a click event listener to the cashoutButton
			const cashoutButton = document.getElementById('cashout-button');

			cashoutButton.addEventListener('click', () => {
				if (!cashoutclicked) {
					cashoutclicked = true;

					const cashOutValue = parseFloat(counterText.text.substring(1));

					const betForm = document.getElementById('bet-form');
					// Send the cashOutValue to the server using an API call

					const formdata = { type: 'cashout_validate', multiplier: cashOutValue, game_id };

					const data = JSON.stringify(formdata);

					groupSocket.send(data);
				}
			});
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

		function CountingComplete(crashpoint) {
			if (counterText) {
				counterText.destroy();
			}

			crashText = scene.add.dynamicBitmapText(400, 200, 'desyrel').setOrigin(0.5, 0);
			crashText.setText('Popped at x' + crashpoint);
		}
	}
}
