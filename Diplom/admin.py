from Diplom.models import Projects
from Diplom.models import Comments
from Diplom.models import Message
from Diplom.models import Chat
from Diplom.models import Like
from Diplom.models import Theme
from Diplom.models import Type
from django.contrib import admin

admin.site.register(Projects)
admin.site.register(Comments)
admin.site.register(Like)
admin.site.register(Theme)
admin.site.register(Type)
admin.site.register(Chat)
admin.site.register(Message)
