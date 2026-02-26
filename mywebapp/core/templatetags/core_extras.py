from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    try:
        # Pokušaj da konvertuješ key u int ako je dictionary sa int ključevima
        if isinstance(key, str) and key.isdigit():
            return dictionary.get(int(key), 0)
        return dictionary.get(key, 0)
    except (AttributeError, TypeError):
        # Ako dictionary nije dict ili nema taj ključ
        return 0