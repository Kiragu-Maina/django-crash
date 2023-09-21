
      
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
                url: register,  // Replace with your actual login URL
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
  