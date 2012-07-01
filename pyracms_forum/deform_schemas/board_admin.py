from colander import SequenceSchema, SchemaNode, String, Schema, deferred

class ForumCategoryItem(SequenceSchema):
    name = SchemaNode(String())

class ForumCategory(Schema):
    forum_categories = ForumCategoryItem()

@deferred
def deferred_default_forum_name(node, kw):
    forum = kw.get('forum')
    if kw.get('name'):
        return kw.get('name')
    if forum:
        return forum.name
    else:
        return ''

@deferred
def deferred_default_forum_description(node, kw):
    forum = kw.get('forum')
    if forum:
        return forum.description
    else:
        return ''

class EditForum(Schema):
    name = SchemaNode(String(), default=deferred_default_forum_name)
    description = SchemaNode(String(),
                             default=deferred_default_forum_description)
