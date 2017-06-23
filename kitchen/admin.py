from django.contrib import admin

from kitchen.models import ProcessedProduct, Warehouse, Delivery, DeliveryList


@admin.register(ProcessedProduct)
class AdminProcessedCartridge(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'status', 'ticket')
    list_display_links = ('id', 'created_at')
    raw_id_fields = ('ticket',)
    search_fields = ('id', 'ticket__id',)
    ordering = ('-created_at',)


@admin.register(Warehouse)
class AdminWarehouse(admin.ModelAdmin):
    list_display = ('id', 'supply', 'status', 'quantity', 'cost')
    list_display_links = ('id', 'supply')


@admin.register(Delivery)
class AdminDelivery(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    list_display_links = ('id', 'created_at')

@admin.register(DeliveryList)
class AdminDeliveryList(admin.ModelAdmin):
    list_display = ('id', 'delivery', 'supply')
    list_display_links = ('id', 'supply')
