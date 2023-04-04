from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin
from .models import stockList
from .resources import stockResource

@admin.register(stockList)
class PersonAdmin(ImportExportModelAdmin):
 list_display = ('stockId','stockName')
 resource_class = stockResource