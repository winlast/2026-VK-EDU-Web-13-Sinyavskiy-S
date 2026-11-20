from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


admin.site.unregister(User)


@admin.register(User)
class ForumUserAdmin(UserAdmin):
    inlines = [ProfileInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_avatar')
    search_fields = ('user__username', 'user__email')
    list_filter = (('avatar', admin.EmptyFieldListFilter),)
    list_select_related = ('user',)
    raw_id_fields = ('user',)

    @admin.display(boolean=True, description='Аватар загружен')
    def has_avatar(self, profile):
        return bool(profile.avatar)
