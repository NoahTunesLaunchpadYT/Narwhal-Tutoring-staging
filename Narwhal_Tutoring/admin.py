from django.contrib import admin
from .models import *

# Register your models here.
#admin.site.register(User_details)
admin.site.register(Subject)
admin.site.register(Availability)
admin.site.register(Cart)
admin.site.register(Lesson)
admin.site.register(User_details)

class PriceInlineAdmin(admin.TabularInline):
    model = Price
    extra = 0
 
class ProductAdmin(admin.ModelAdmin):
    inlines = [PriceInlineAdmin]
 
admin.site.register(Product, ProductAdmin)

class DetailsInlineAdmin(admin.StackedInline):
    model = User_details
    extra = 0
 
class UserAdmin(admin.ModelAdmin):
    inlines = [DetailsInlineAdmin]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
