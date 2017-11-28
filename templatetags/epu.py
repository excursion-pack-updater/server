from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def set(context, *values, **kwargs):
    name = next(node for node in context["block"].nodelist if node.__class__.__name__ == "SimpleNode").args[0].var.var
    
    if kwargs.get("default", False):
        value = context.get(name, None)
        
        if value != None:
            return ""
    
    value = kwargs.get("sep", " ").join(values[1:])
    context.dicts[-2][name] = value #set value in the context passed to render function
    
    return ""
