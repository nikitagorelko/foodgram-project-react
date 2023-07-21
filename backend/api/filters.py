from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def get_is_favorited(self, queryset, name, value):
        del name
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(recipe_in_favorite__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        del name
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(recipe_in_cart__user=user)
        return queryset
