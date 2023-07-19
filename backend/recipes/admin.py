from django.contrib import admin

from recipes.models import Tag, Ingredient, Recipe, RecipeTag, RecipeIngredient, Favorite, ShoppingCart

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeTag)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)