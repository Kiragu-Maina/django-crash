
document.addEventListener('DOMContentLoaded', function () {

  
    const gameConfig = {
        type: Phaser.AUTO,
        scale: {
            mode: Phaser.Scale.FIT,
            parent: 'game-container',
            width: 800,
            height: 600
        },
        
       
        transparent: true,
        fps: {
            target: 30,
            forceSetTimeOut: true
            },
        scene: [Example],
        
    }

    const game = new Phaser.Game(gameConfig);
   
    
});
