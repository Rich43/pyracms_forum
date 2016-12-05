from colander import MappingSchema, SchemaNode, String, deferred
from deform.widget import TextAreaWidget, TextInputWidget, HiddenWidget

@deferred
def deferred_default_title(node, kw):
    if kw.get('thread_name'):
        return kw.get('thread_name')
    else:
        return ''

@deferred
def deferred_default_description(node, kw):
    if kw.get('description'):
        return kw.get('description')
    else:
        return ''

@deferred
def deferred_default_body(node, kw):
    if kw.get('body'):
        return kw.get('body')
    else:
        return ''

class ThreadSchema(MappingSchema):
    title = SchemaNode(String(), default=deferred_default_title,
                       widget=TextInputWidget(), location="body", type='str')
    description = SchemaNode(String(), default=deferred_default_description,
                             widget=TextInputWidget(), location="body",
                             type='str')
    body = SchemaNode(String(), default='', location="body", type='str',
                      widget=TextAreaWidget(rows=5, cols=80))


class ThreadSchemaAPI(MappingSchema):
    title = SchemaNode(String(), default=deferred_default_title,
                       widget=TextInputWidget(), location="body", type='str')
    description = SchemaNode(String(), default=deferred_default_description,
                             widget=TextInputWidget(), location="body",
                             type='str')

class PostSchema(MappingSchema):
    title = SchemaNode(String(), default=deferred_default_title,
                       widget=TextInputWidget(), location="body", type='str')
    body = SchemaNode(String(), default=deferred_default_body,
                      widget=TextAreaWidget(rows=5, cols=80),
                      location="body", type='str')

class QuickReplySchema(MappingSchema):
    title = SchemaNode(String(), default=deferred_default_title,
                       widget=HiddenWidget())
    body = SchemaNode(String(), title='', default='',
                      widget=TextAreaWidget(rows=5, cols=80))