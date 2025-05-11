from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(AttributeType)
admin.site.register(AttributeOption)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductItem)
admin.site.register(Image)