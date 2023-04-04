from django.db import models

# Create your models here.

class stockList(models.Model):
    stockId = models.CharField(max_length=10, primary_key=True)  #股票代號
    stockName = models.CharField(max_length=10) #股票名稱
    def __str__(self):
        return self.stockId + '-' + self.stockName
    
