from django.db import models
from signals_auth.models import MT5Account, MT5Account_Symbols

trade_results = {
    ("profit", "profit"),
    ("loss", "loss")
}
class Trade_History(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(MT5Account, on_delete=models.CASCADE, null=True)
    symbol = models.CharField(max_length=100)
    stop_loss = models.FloatField()
    take_profit = models.FloatField()
    price = models.FloatField()
    type = models.CharField(max_length=100)
    result = models.CharField(max_length=15, choices=trade_results, blank=True)

    def __str__(self):
        return str(self.id)
    
class Trade_Task(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    account = models.OneToOneField(MT5Account_Symbols, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return str(self.id)
    

    


