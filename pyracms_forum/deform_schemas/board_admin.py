from colander import SequenceSchema, SchemaNode, String, Schema, deferred

class ForumCategoryItem(SequenceSchema):
    name = SchemaNode(String(), location="body", type='str')

class ForumCategoryItemAPI(Schema):
    name = SchemaNode(String(), location="body", type='str')

class UpdateForumCategory(Schema):
    old_name = SchemaNode(String(), location="body", type='str')
    new_name = SchemaNode(String(), location="body", type='str')

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
    name = SchemaNode(String(), default=deferred_default_forum_name,
                      location="body", type='str')
    description = SchemaNode(String(), location="body", type='str',
                             default=deferred_default_forum_description)

class EditForumAPI(EditForum):
    category = SchemaNode(String(), location="body", type='str')