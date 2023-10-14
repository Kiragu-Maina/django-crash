
      
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
                  url: login,  // Replace with your actual login URL
                  type: 'POST',
                  data: data,
                  success: function (response, status, xhr) {
                      // Handle the response from the server, e.g., redirect or show a success message
                      console.log('here');
                      console.log(response);
                      var newCsrfToken = getCookie("csrftoken");
                      console.log('newcsrf,', newCsrfToken);

                      // Update the CSRF token in your JavaScript code
                      if (newCsrfToken) {
                          // Assuming you have a function to update the CSRF token
                          updateCsrfToken(newCsrfToken);
                      }
                      updateNavigationMenu(true, response.balance, response.username)
                      const loginmodal = document.getElementById("closeloginmodal")
                      loginmodal.click();
                      $("#login_submit_btn").show();
                    $("#spinner1").hide();
                      
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
                url: register,  // Replace with your actual login URL
                type: 'POST',
                data: data,
                success: function (response, xhr, status) {
                    // Handle the response from the server, e.g., redirect or show a success message
                    console.log(response);
                    var newCsrfToken = getCookie("csrftoken");

                    // Update the CSRF token in your JavaScript code
                    if (newCsrfToken) {
                        // Assuming you have a function to update the CSRF token
                        updateCsrfToken(newCsrfToken);
                    }
                    updateNavigationMenu(true, response.balance, response.username)
                    $("#register_submit_btn").show();
                    $("#spinner2").hide();
                    const registermodal = document.getElementById("closeregistermodal")
                    registermodal.click();
                    
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
                url: deposit,  // Replace with your actual login URL
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
                url: withdraw,  // Replace with your actual login URL
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
      function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }
      function updateCsrfToken(newToken) {
        var csrfTokenDiv = document.getElementById("csrf_token");
	      var csrfToken = csrfTokenDiv.querySelector("[name=csrfmiddlewaretoken]")
        if (csrfToken) {
            csrfToken.setAttribute('value', newToken);
        }
    }
  
      function updateNavigationMenu(isAuthenticated, balance = null, username) {
        const navMenu = document.getElementById('nav-menu');
        const side_bar = document.getElementById('side-bar');
        const user_name = document.getElementById('user-name');

        
        if (isAuthenticated) {
            // User is authenticated, update the menu
            user_name.innerHTML = username
            navMenu.innerHTML = `
                <ul class="navbar-nav justify-content-end">
                    <li class="nav-item d-flex align-items-center">
                        <a class="nav-link" href="#ex3" rel="modal:open">
                            <i class="fa fa-money me-sm-1"></i>
                            <span class="nav-link text-white font-weight-bold px-0">Deposit</span>
                        </a>
                    </li>
                    <li class="nav-item d-flex align-items-center">
                        <a class="nav-link" href="#ex4" rel="modal:open">
                            <i class="fa fa-credit-card me-sm-1"></i>
                            <span class="nav-link text-white font-weight-bold px-0">Withdraw</span>
                        </a>
                    </li>
                    <li class="nav-item d-flex align-items-center">
                        <span class="nav-link text-white font-weight-bold px-0" id="balance">Balance: ${balance}</span>
                    </li>
                </ul>
            `;
          side_bar.innerHTML = `
            <li class="nav-item">
              <a class="nav-link " href=${logout}>
                <div class="icon icon-shape icon-sm border-radius-md text-center me-2 d-flex align-items-center justify-content-center">
                  <i class="ni ni-collection text-info text-sm opacity-10"></i>
                </div>
                <span class="nav-link-text ms-1">Log out</span>
              </a>
            </li>
           `
            
            
           
            

        } else {
            // User is not authenticated, update the menu
            navMenu.innerHTML = `
                <ul class="navbar-nav justify-content-end">
                    <li class="nav-item d-flex align-items-center">
                        <a href="#ex1" rel="modal:open" class="nav-link text-white font-weight-bold px-2">
                            <i class="fa fa-user me-sm-1"></i>
                            <span class="nav-link text-white font-weight-bold px-0">Sign In</span>
                        </a>
                    </li>
                    <li class="nav-item d-flex align-items-center">
                        <a href="#ex2" rel="modal:open" class="nav-link text-white font-weight-bold px-2">
                            <i class="fa fa-user-plus me-sm-1"></i>
                            <span class="nav-link text-white font-weight-bold px-0">Register</span>
                        </a>
                    </li>
                </ul>
            `;
            side_bar.innerHTML = `
                      <li class="nav-item">
                      <a class="nav-link"  href="#ex1" rel="modal:open">
                      
                        <div class="icon icon-shape icon-sm border-radius-md text-center me-2 d-flex align-items-center justify-content-center">
                          <i class="ni ni-single-copy-04 text-warning text-sm opacity-10"></i>
                        </div>
                        <span class="nav-link-text ms-1">Sign In</span>
                      </a>
                    </li>
                    <li class="nav-item">
                      <a class="nav-link " href="#ex2" rel="modal:open">
                        <div class="icon icon-shape icon-sm border-radius-md text-center me-2 d-flex align-items-center justify-content-center">
                          <i class="ni ni-collection text-info text-sm opacity-10"></i>
                        </div>
                        <span class="nav-link-text ms-1">Register</span>
                      </a>
                    </li>`;
        }
    }
    