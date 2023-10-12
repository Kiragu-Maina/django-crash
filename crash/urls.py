from django.urls import path
from .views import *
urlpatterns = [
    path("", Home.as_view(), name="home"),
    path('get-new-crash-point/', get_new_crash_point, name='get_new_crash_point'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('placebet/', PlaceBet.as_view(), name='placebet'),
    path('cashout/', CashoutView.as_view(), name='cashout'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('adminpage/', AdminView.as_view(), name='adminpage'),
    path('start_game/', StartGameView.as_view(), name='start_game'),
    path('balloon_chosen/', BalloonChosenView.as_view(), name='balloon_chosen' ),
    path('simulate_users/', TestView.as_view(), name='simulate_users'),
    path('download-users-json/', download_users_json, name='download_users_json'),
    path('respawn/', AdminViewWithRespawn.as_view(), name='respawn'),
    path('top_winners', TopWinnersView.as_view(), name='top_winners'),
    path('user_bets', UserBetsView.as_view(), name='user_bets')
    
       

]
