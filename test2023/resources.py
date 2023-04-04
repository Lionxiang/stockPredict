from import_export import resources
from test2023.models import stockList

class stockResource(resources.ModelResource):
    class Meta:
        model = stockList
        skip_unchanged = True
        report_skipped = True
        exclude = ('id',)
        import_id_fields=('stockId',)
        # export_order = ('stockId', 'stockName')