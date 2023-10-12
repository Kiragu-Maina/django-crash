var balloon = "{% static 'assets/balloon.png' %}";
  var balloon1 = "{% static 'assets/balloon1.png' %}";
  var balloon2 = "{% static 'assets/balloon2.png' %}";
  var balloon3 = "{% static 'assets/balloon3.png' %}";
  var balloon4 = "{% static 'assets/balloon4.png' %}";




  
  var pumpdown = "{% static 'assets/pump1.png' %}";
  var pumpup = "{% static 'assets/pump2.png' %}";
  var space = "{% static 'assets/space.png' %}";
  
 
  var popped = "{% static 'assets/popped.png' %}";

  const body = document.getElementsByTagName('body')[0];
  const hr = document.querySelectorAll('div:not(.sidenav) > hr');
  const sidebar = document.querySelector('.sidenav');
  const sidebarWhite = document.querySelectorAll('.sidenav.bg-white');
  const hr_card = document.querySelectorAll('div:not(.bg-gradient-dark) hr');
  const text_btn = document.querySelectorAll('button:not(.btn) > .text-dark');
  const text_span = document.querySelectorAll('span.text-dark, .breadcrumb .text-dark');
  const text_span_white = document.querySelectorAll('span.text-white');
  const text_strong = document.querySelectorAll('strong.text-dark');
  const text_strong_white = document.querySelectorAll('strong.text-white');
  const text_nav_link = document.querySelectorAll('a.nav-link.text-dark');
  const secondary = document.querySelectorAll('.text-secondary');
  const bg_gray_100 = document.querySelectorAll('.bg-gray-100');
  const bg_gray_600 = document.querySelectorAll('.bg-gray-600');
  const btn_text_dark = document.querySelectorAll('.btn.btn-link.text-dark, .btn .ni.text-dark');
  const btn_text_white = document.querySelectorAll('.btn.btn-link.text-white, .btn .ni.text-white');
  const card_border = document.querySelectorAll('.card.border');
  const card_border_dark = document.querySelectorAll('.card.border.border-dark');
  const svg = document.querySelectorAll('g');
  const navbarBrand = document.querySelector('.navbar-brand-img');
  const navbarBrandImg = navbarBrand.src;
  const navLinks = document.querySelectorAll('.navbar-main .nav-link, .navbar-main .breadcrumb-item, .navbar-main .breadcrumb-item a, .navbar-main h6');
  const cardNavLinksIcons = document.querySelectorAll('.card .nav .nav-link i');
  const cardNavSpan = document.querySelectorAll('.card .nav .nav-link span');


  
    body.classList.add('dark-version');
    if (navbarBrandImg.includes('logo-ct-dark.png')) {
      var navbarBrandImgNew = navbarBrandImg.replace("logo-ct-dark", "logo-ct");
      navbarBrand.src = navbarBrandImgNew;
    }
    for (var i = 0; i < cardNavLinksIcons.length; i++) {
      if (cardNavLinksIcons[i].classList.contains('text-dark')) {
        cardNavLinksIcons[i].classList.remove('text-dark');
        cardNavLinksIcons[i].classList.add('text-white');
      }
    }
    for (var i = 0; i < cardNavSpan.length; i++) {
      if (cardNavSpan[i].classList.contains('text-sm')) {
        cardNavSpan[i].classList.add('text-white');
      }
    }
    for (var i = 0; i < hr.length; i++) {
      if (hr[i].classList.contains('dark')) {
        hr[i].classList.remove('dark');
        hr[i].classList.add('light');
      }
    }
    for (var i = 0; i < hr_card.length; i++) {
      if (hr_card[i].classList.contains('dark')) {
        hr_card[i].classList.remove('dark');
        hr_card[i].classList.add('light');
      }
    }
    for (var i = 0; i < text_btn.length; i++) {
      if (text_btn[i].classList.contains('text-dark')) {
        text_btn[i].classList.remove('text-dark');
        text_btn[i].classList.add('text-white');
      }
    }
    for (var i = 0; i < text_span.length; i++) {
      if (text_span[i].classList.contains('text-dark')) {
        text_span[i].classList.remove('text-dark');
        text_span[i].classList.add('text-white');
      }
    }
    for (var i = 0; i < text_strong.length; i++) {
      if (text_strong[i].classList.contains('text-dark')) {
        text_strong[i].classList.remove('text-dark');
        text_strong[i].classList.add('text-white');
      }
    }
    for (var i = 0; i < text_nav_link.length; i++) {
      if (text_nav_link[i].classList.contains('text-dark')) {
        text_nav_link[i].classList.remove('text-dark');
        text_nav_link[i].classList.add('text-white');
      }
    }
    for (var i = 0; i < secondary.length; i++) {
      if (secondary[i].classList.contains('text-secondary')) {
        secondary[i].classList.remove('text-secondary');
        secondary[i].classList.add('text-white');
        secondary[i].classList.add('opacity-8');
      }
    }
    for (var i = 0; i < bg_gray_100.length; i++) {
      if (bg_gray_100[i].classList.contains('bg-gray-100')) {
        bg_gray_100[i].classList.remove('bg-gray-100');
        bg_gray_100[i].classList.add('bg-gray-600');
      }
    }
    for (var i = 0; i < btn_text_dark.length; i++) {
      btn_text_dark[i].classList.remove('text-dark');
      btn_text_dark[i].classList.add('text-white');
    }
    for (var i = 0; i < sidebarWhite.length; i++) {
      sidebarWhite[i].classList.remove('bg-white');
    }
    for (var i = 0; i < svg.length; i++) {
      if (svg[i].hasAttribute('fill')) {
        svg[i].setAttribute('fill', '#fff');
      }
    }
    for (var i = 0; i < card_border.length; i++) {
      card_border[i].classList.add('border-dark');
    }
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
            scene: [Example],
            
        }

        const game = new Phaser.Game(gameConfig);
       
        
    });
     // Wait for the DOM to be ready
     document.addEventListener("DOMContentLoaded", function () {
        // Get all the amount buttons
        const amountButtons = document.querySelectorAll(".amount-btn");
        // Get the input field
        const selectedAmountInput = document.getElementById("selected-amount");
        const betButton = document.getElementById("bet-button");
        const errorText = document.getElementById("error-text")
        betButton.disabled = false;


        // Add click event listeners to each amount button
        amountButtons.forEach(function (button) {
            button.addEventListener("click", function () {
                // Get the data-amount attribute value from the button
                const amount = button.getAttribute("data-amount");
                // Update the input field value with the selected amount
                selectedAmountInput.value = amount;
                betButton.textContent = `BET (${amount})`;
            });
        });
        selectedAmountInput.addEventListener("input", function () {
          const selectedAmount = selectedAmountInput.value;
          betButton.textContent = `BET (${selectedAmount})`;
      });

        // Prevent the form from submitting when the "BET" button is clicked
        const betForm = document.getElementById("bet-form");
        const betAmountInput = document.getElementById("betAmount");
        betAmountInput.value = selectedAmountInput.value;
        const hideErrorandResetBet = () => {
          errorText.style.display = 'none';
          errorText.innerHTML = '';
          betButton.textContent = 'BET';
      };
        betForm.addEventListener("submit", function (event) {
          event.preventDefault();
      
          const formData = new FormData();
          formData.append('bet_amount', selectedAmountInput.value);
          if (window.roomName){
            formData.append('group_name', window.roomName);
          }
          else {
            formData.append('group_name', 'group_1');
          }
          
          
          const csrfToken = betForm.querySelector('[name=csrfmiddlewaretoken]').value;
      
          fetch('placebet/', {
              method: 'POST',
              headers: {
                  'X-CSRFToken': csrfToken
              },
              body: formData
          })
          .then(response => response.json())
          .then(data => {
              console.log('data sent', data);
              if (data.status == 'success'){
                window.globalBetAmount = parseFloat(data.bet_amount);
                betButton.textContent = `BET Placed`;
                betButton.disabled = true;
              }
              else{
              betButton.textContent = 'BET Not Placed';
              errorText.innerHTML = data.message;
              errorText.style.display = 'block';
              setTimeout(hideErrorandResetBet, 5000); 
              
              }// Update the page content using the data received from the server
              // For example, update the user's balance or display a success message
          })
          .catch(error => {
              console.error('Error:', error);
          });
        });
       
      });
      
      $(document).ready(function () {
        const error = document.getElementById("error")

          $('#login_submit_btn').click(function () {
            $("#login_submit_btn").hide();
          $("#spinner1").show();
              var phone_number = $('#phone_number1').val();

              var password = $('#password').val();
              var csrf_token = $("input[name=csrfmiddlewaretoken]").val();  // Get the CSRF token
  
              // Prepare the data to be sent
              var data = {
                  username: phone_number,
                  password: password,
                  csrfmiddlewaretoken: csrf_token
              };
  
              // Send an AJAX POST request to the server
              $.ajax({
                  url: '{% url "login" %}',  // Replace with your actual login URL
                  type: 'POST',
                  data: data,
                  success: function (response) {
                      // Handle the response from the server, e.g., redirect or show a success message
                      console.log('here');
                      console.log(response);
                      location.reload();
                      
                  },
                  error: function (xhr, status, error) {
                      // Handle errors, e.g., display an error message
                      try {
                        var errorResponse = JSON.parse(xhr.responseText);
                        console.log(errorResponse)
                        var errorMessage = errorResponse.errors.__all__[0];
                        console.log(errorMessage);
                        $("#error1").html(errorMessage);
                      } catch (e) {
                          // Handle JSON parsing error or other issues
                          console.error(e);
                          $("#error1").html("An error occurred.");
                      }
                      $("#login_submit_btn").show();
                    $("#spinner1").hide();
                  }
              });
          });
          $('#register_submit_btn').click(function () {
            $("#register_submit_btn").hide();
           $("#spinner2").show();
            var phone_number = $('#phone_number2').val();
            var username = $('#user_name').val();

            var password1 = $('#password1').val();
            var password2 = $('#password2').val();
            var csrf_token = $("input[name=csrfmiddlewaretoken]").val();  // Get the CSRF token

            // Prepare the data to be sent
            var data = {
                user_name: username,
                phone_number: phone_number,
                password1: password1,
                password2: password2,

                csrfmiddlewaretoken: csrf_token
            };

            // Send an AJAX POST request to the server
            $.ajax({
                url: '{% url "register" %}',  // Replace with your actual login URL
                type: 'POST',
                data: data,
                success: function (response) {
                    // Handle the response from the server, e.g., redirect or show a success message
                    console.log(response);
                    location.reload();
                    
                },
                error: function (xhr, status, error) {
                    try {
                      var errorResponse = JSON.parse(xhr.responseText);
                      console.log(errorResponse)
                      var errorMessage = errorResponse.errors.__all__[0];
                      console.log(errorMessage);
                      $("#error2").html(errorMessage);
                    } catch (e) {
                        // Handle JSON parsing error or other issues
                        console.error(e);
                        $("#error2").html("An error occurred.");
                    }
                    $("#register_submit_btn").show();
                    $("#spinner2").hide();
                }
            });
        });
        $('#deposit_btn').click(function () {
          $("#deposit_btn").hide();
        $("#spinner3").show();
            var deposit_amount = $('#deposit_amount').val();

            
            var csrf_token = $("input[name=csrfmiddlewaretoken]").val();  // Get the CSRF token

            // Prepare the data to be sent
            var data = {
                deposit_amount: deposit_amount,
                
                csrfmiddlewaretoken: csrf_token
            };

            // Send an AJAX POST request to the server
            $.ajax({
                url: '{% url "deposit" %}',  // Replace with your actual login URL
                type: 'POST',
                data: data,
                success: function (response) {
                    // Handle the response from the server, e.g., redirect or show a success message
                    console.log('here');
                    console.log(response);
                    $("#error3").html('deposit successful');
                    $("#spinner3").hide();
                    $("#deposit_btn").show();
                    
                },
                error: function (xhr, status, error) {
                    // Handle errors, e.g., display an error message
                    try {
                      var errorResponse = JSON.parse(xhr.responseText);
                      console.log(errorResponse)
                      var errorMessage = errorResponse.errors.__all__[0];
                      console.log(errorMessage);
                      $("#error3").html(errorMessage);
                    } catch (e) {
                        // Handle JSON parsing error or other issues
                        console.error(e);
                        $("#error3").html("An error occurred.");
                    }
                    $("#deposit_btn").show();
                  $("#spinner3").hide();
                }
            });
        });
        $('#withdraw_btn').click(function () {
          $("#withdraw_btn").hide();
        $("#spinner4").show();
            var withdraw_amount = $('#withdraw_amount').val();

            
            var csrf_token = $("input[name=csrfmiddlewaretoken]").val();  // Get the CSRF token

            // Prepare the data to be sent
            var data = {
                withdraw_amount: withdraw_amount,
                
                csrfmiddlewaretoken: csrf_token
            };

            // Send an AJAX POST request to the server
            $.ajax({
                url: '{% url "withdraw" %}',  // Replace with your actual login URL
                type: 'POST',
                data: data,
                success: function (response) {
                    // Handle the response from the server, e.g., redirect or show a success message
                    console.log('here');
                    console.log(response);
                    $("#error4").html('Withdrawal successful');
                    $("#spinner4").hide();
                    $("#withdraw_btn").show();
                    
                    
                },
                error: function (xhr, status, error) {
                    // Handle errors, e.g., display an error message
                    try {
                      var errorResponse = JSON.parse(xhr.responseText);
                      console.log(errorResponse)
                      var errorMessage = errorResponse.errors.__all__[0];
                      console.log(errorMessage);
                      $("#error4").html(errorMessage);
                    } catch (e) {
                        // Handle JSON parsing error or other issues
                        console.error(e);
                        $("#error4").html("An error occurred.");
                    }
                    $("#withdraw_btn").show();
                  $("#spinner4").hide();
                }
            });
        });
      });