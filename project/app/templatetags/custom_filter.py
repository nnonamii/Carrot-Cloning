from django import template

register = template.Library()

@register.filter
def custom_filter(value):
    # 여기에 필터 로직을 작성합니다.
    return transformed_value
