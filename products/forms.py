# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django import forms

from products.models import Supply, SuppliesCategory, Cartridge, CartridgeRecipe, Presentation
from kitchen.models import Warehouse, ShopListDetail
from branchoffices.models import Supplier


class SupplyForm(forms.ModelForm):

    class Meta:
        model = Supply
        fields = '__all__'

class SuppliesCategoryForm(forms.ModelForm):

    class Meta:
        model = SuppliesCategory
        fields = '__all__'

class SuppliersForm(forms.ModelForm):

    class Meta:
        model = Supplier
        fields = '__all__'


class CartridgeForm(forms.ModelForm):

    class Meta:
        model = Cartridge
        fields = '__all__'

class RecipeForm(forms.ModelForm):

    class Meta:
        model = CartridgeRecipe
        fields = '__all__'

class WarehouseForm(forms.ModelForm):

    class Meta:
        model = Warehouse
        fields = '__all__'

class PresentationForm(forms.ModelForm):

    class Meta:
        model = Presentation
        fields = '__all__'


class ShopListDetailForm(forms.ModelForm):

    class Meta:
        model = ShopListDetail
        fields = '__all__'