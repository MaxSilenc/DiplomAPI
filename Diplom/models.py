from django.db import models


class Projects(models.Model):
    headline_name = models.CharField(max_length=30)
    name = models.CharField(max_length=20)
    img = models.ImageField(upload_to='img')
    text = models.TextField()
    project = models.FileField(default='default.txt')
    theme_id = models.CharField(max_length=20, default=1)
    type = models.CharField(max_length=20, default=1)

    def delete(self, *args, **kwargs):
        self.img.delete()
        super().delete(*args, **kwargs)


class Comments(models.Model):
    author = models.CharField(max_length=30)
    project_id = models.CharField(max_length=20)
    text = models.TextField()


class Like(models.Model):
    author = models.CharField(max_length=30)
    project_id = models.CharField(max_length=20)
    like = models.CharField(max_length=1)


class Theme(models.Model):
    name = models.CharField(max_length=30)


class Type(models.Model):
    name = models.CharField(max_length=30)