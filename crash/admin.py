from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Transactions, User, Games, Bank, Clients, OwnersBank, TransactionsForLastGameBet
from .forms import UserChangeForm, UserCreationForm  # Import your UserChangeForm and UserCreationForm

@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    # Customize the display and behavior of the Transactions model in the admin
    list_display = ('user', 'bet', 'multiplier', 'won')
    list_filter = ('user',)

class CustomUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('phone_number', 'user_name', 'is_active', 'is_admin')
    list_filter = ('is_active', 'is_admin')
    fieldsets = (
        (None, {'fields': ('user_name', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superuser', 'last_login', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('user_name', 'phone_number', 'password1', 'password2')}),
    )
    search_fields = ('phone_number', 'user_name')
    ordering = ('phone_number',)
    filter_horizontal = ('groups', 'user_permissions')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        if not is_superuser:
            disabled_fields = {"is_superuser", "user_permissions", "groups", "is_staff"}
            for f in disabled_fields:
                if f in form.base_fields:
                    form.base_fields[f].disabled = True
        return form

class BankAdmin(admin.ModelAdmin):
    readonly_fields = ('account_id',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Games)
admin.site.register(Bank, BankAdmin)
admin.site.register(OwnersBank)
admin.site.register(Clients)
admin.site.register(TransactionsForLastGameBet)
