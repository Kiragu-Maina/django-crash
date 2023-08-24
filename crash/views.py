from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import Transactions
from .utils import ServerSeedGenerator

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import FormView, View
from .forms import UserCreationForm, UserLoginForm
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
import random
import string
from .backends import PhoneUsernameAuthenticationBackend as EoP

class UserRegistrationView(SuccessMessageMixin, CreateView):
    form_class = UserCreationForm
    template_name = 'sign-up.html'
    success_url = reverse_lazy('login')  # Redirect to login page after successful registration
    success_message = "Your account has been created successfully. You can now log in."

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your registration. Please check the form and try again.')
        return self.render_to_response(self.get_context_data(form=form))

class UserLoginView(SuccessMessageMixin, FormView):
    form_class = UserLoginForm
    template_name = 'sign-in.html'
    success_url = ('')  # Redirect to home page after successful login
    success_message = "You have successfully logged in!"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            print('authenticated')
            return redirect('/')  # Redirect authenticated user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return redirect('/')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid phone number or password. Please try again.')
        return self.render_to_response(self.get_context_data(form=form))

    def redirect_to_success_url(self):
        success_url = self.success_url
        print(success_url)
        
        return self.render_to_response(self.get_context_data(success_url=success_url))
    
class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/login')  

def get_new_crash_point(request):
    seed_generator = ServerSeedGenerator()
    seed_generator.generate_hash()
    seed_generator.crash_point_from_hash()
    
    crash_point = seed_generator.get_crash_point()
    
    return JsonResponse({'crash_point': crash_point})
class Home(TemplateView):
    model = Transactions
    template_name = 'index.html'
    context_object_name = 'items'

   

    def get_context_data(self, **kwargs):
        # Fetch and add the Transactions objects to the context
        def generate_random_string(length):
            letters = string.ascii_letters  # Get all letters (both lowercase and uppercase)
            random_string = ''.join(random.choice(letters) for _ in range(length))
            return random_string

        if self.request.user.is_authenticated:
            username = self.request.user.user_name
        else:
            username = generate_random_string(8)
        items = self.model.objects.all()

       
        context = super().get_context_data(**kwargs)
       
        context['items'] = items
        context['username'] = username

        # Logging and debugging
       

        return context
