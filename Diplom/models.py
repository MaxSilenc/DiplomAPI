from django.db import models


class Projects(models.Model):
    headline_name = models.CharField(max_length=30)
    name = models.CharField(max_length=20)
    img = models.ImageField(upload_to='img')
    img2 = models.ImageField(upload_to='img', default='img.img')
    img3 = models.ImageField(upload_to='img', default='img.img')
    text = models.TextField()
    project = models.FileField(default='default.txt')
    theme_id = models.CharField(max_length=20, default=1)
    type = models.CharField(max_length=20, default=1)
    in_work = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.img.delete()
        super().delete(*args, **kwargs)


class Comments(models.Model):
    author = models.CharField(max_length=30)
    project_id = models.CharField(max_length=20)
    text = models.TextField()


class Message(models.Model):
    author = models.CharField(max_length=30)
    chat_id = models.CharField(max_length=20)
    text = models.TextField()


class Like(models.Model):
    author = models.CharField(max_length=30)
    project_id = models.CharField(max_length=20)
    like = models.CharField(max_length=1)


class Theme(models.Model):
    name = models.CharField(max_length=30)


class Type(models.Model):
    name = models.CharField(max_length=30)


class Chat(models.Model):
    username = models.CharField(max_length=30)
    adminname = models.CharField(max_length=30)


class ProjectInWork(models.Model):
    user_id = models.CharField(max_length=20)
    project_id = models.CharField(max_length=20)
