from .models import Projects
from django.forms import ModelForm
from django.contrib.auth.models import User


class ProjectsForm(ModelForm):
    class Meta:
        model = Projects
        fields = ['name', 'headline_name', 'img', 'text', 'project']

class ChangePasswordForm(ModelForm):
    class Meta:
        model = User
        fields = ['password']

