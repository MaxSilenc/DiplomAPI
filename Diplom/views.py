from django.shortcuts import render, redirect
from Diplom.models import Projects, Comments, Like, Theme, Type
from django.template.context_processors import csrf
from django.contrib import auth
from .forms import ProjectsForm, ChangePasswordForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import os
import shutil

from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import viewsets
from .serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
import re


def test(request):
    all_items = Projects.objects.all()
    return render(request, 'listOfUE4/index.html', {'object_list': all_items, 'username': auth.get_user(request).username})


def main(request):
    return render(request, 'main/index.html', {'username': auth.get_user(request).username})


def auto(request):
    return render(request, 'auto/index.html', {'username': auth.get_user(request).username})


def login(request):
    args = {}
    args.update(csrf(request))
    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            args['login_error'] = 'Неверно введены данные'
            return render(request, 'auto/index.html', args)


def logout(request):
    auth.logout(request)
    return redirect('/')


def adminPanel(request):
    return render(request, 'adminPanel/index.html', {'username': auth.get_user(request).username})


def adminPanelProjectList(request):
    all_items = Projects.objects.all()
    return render(request, 'adminPanel/ProjectList/index.html', {'object_list': all_items, 'username': auth.get_user(request).username})


def adminPanelDelProject(request):
    if request.method == 'POST':
        del_item = Projects.objects.get(id=request.POST['id'])
        files_dir_name = del_item.name

        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Ue4Project/' + files_dir_name)
        path = path.replace('\\' + 'Diplom' + '\\', '\\' + 'media' + '\\')

        shutil.rmtree(path)
        del_item.delete()

    return redirect('/adminPanel/ProjectList/')


def adminPanelAddProject(request):
    if request.method == 'POST':
        form = ProjectsForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = request.FILES.getlist('project')
            fs = FileSystemStorage()
            form.save()
            for item in myfile:
                filename = fs.save('Ue4Project/' + request.POST['name'] + '/' + item.name, item)
            fs.delete(myfile[-1].name)

            return redirect('/adminPanel/ProjectList/')
        else:
            msg = 'error'
            form = ProjectsForm()
            data = {'form': form, 'msg': msg, 'username': auth.get_user(request).username}
            return render(request, 'adminPanel/ProjectList/add/index.html', data)
    else:
        form = ProjectsForm()
        data = {'form': form, 'username': auth.get_user(request).username}
        return render(request, 'adminPanel/ProjectList/add/index.html', data)


def adminPanelUsersList(request):
    all_items = User.objects.all()
    return render(request, 'adminPanel/UsersList/index.html', {'object_list': all_items, 'username': auth.get_user(request).username})


def adminPanelAddUser(request):

    u = User.objects.get(username=request.user)
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = request.POST.get("password")
            new_pass = request.POST.get("new_password")
            new_pass_rep = request.POST.get("new_password_repeat")
            if check_password(old_password, u.password):
                if new_pass == new_pass_rep:
                    u.set_password(new_pass)
                    u.save()
                    return redirect('/adminPanel/UsersList/')
                else:
                    return redirect('/')
            else:
                return redirect('/')
    else:
        form = ChangePasswordForm()
        data = {'form': form, 'username': auth.get_user(request).username}
        return render(request, 'adminPanel/UsersList/add/index.html', data)








@api_view(['GET'])
def projects(request, pageNumber, theme_id, type):

    if theme_id == 'all' and type == 'all':
        all_items = Projects.objects.all()
    elif theme_id == 'all' and type != 'all':
        all_items = Projects.objects.filter(type=type)
    elif theme_id != 'all' and type == 'all':
        all_items = Projects.objects.filter(theme_id=theme_id)
    else:
        all_items = Projects.objects.filter(theme_id=theme_id, type=type)

    page = pageNumber
    projects_paginator = Paginator(all_items, 4)

    try:
        projects = projects_paginator.page(page)
    except PageNotAnInteger:
        projects = projects_paginator.page(4)
    except EmptyPage:
        projects = projects_paginator.page(projects_paginator.num_pages)

    returnArr = []

    for item in projects:
        returnArr.append({
            'id': item.id,
            'title': item.headline_name,
            'text': item.text,
            'directLink': 'theme1',
            'img': item.img.url,
            'name': item.name
        })

    project = {
        "items": returnArr,
        "page": page,
        "count": len(all_items)
    }
    return Response(project)


def projectPage(request, id):
    project = Projects.objects.get(id=id)

    projectJson = {
        'id': project.id,
        'title': project.headline_name,
        'text': project.text,
        'directLink': 'theme1',
        'img': project.img.url,
        'name': project.name
    }
    return JsonResponse(projectJson)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['GET', 'POST'])
def curr_user(request):
    if request.POST['key'] != '':
        try:
            token = Token.objects.get(key=request.POST['key'])
        except:
            token = None
        if token is not None:
            curr_user = {
                'login': token.user.username,
                'email': token.user.email,
                'errorKey': 1
            }
            return Response(curr_user)

    curr_user = {
        'errorKey': 0
    }
    return Response(curr_user)


@api_view(['GET', 'PUT', 'POST'])
def comments(request, id):
    if request.method == 'GET':
        all_items = Comments.objects.filter(project_id=id)

        returnArr = []

        for item in all_items:
            returnArr.append({
                'id': item.id,
                'project_id': item.project_id,
                'text': item.text,
                'author': item.author
            })

        comments = {
            "items": returnArr,
        }
        return Response(comments)

    elif request.method == 'PUT':
        old_comment = Comments.objects.get(id=request.POST['id'])
        old_comment.text = request.POST['text']
        if old_comment.text == '':
            old_comment.delete()
        else:
            old_comment.save()
        return Response({'answer': True})

    elif request.method == 'POST':
        new_comment = Comments()
        new_comment.text = request.POST['text']
        new_comment.author = request.POST['author']
        new_comment.project_id = id
        new_comment.save()
        return Response({'answer': True})


@api_view(['POST'])
def loginReact(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        pattern = r"^[a-zA-Z0-9]{1,100}[@][a-z]{2,6}\.[a-z]{2,4}"
        number_re = re.compile(pattern)
        if number_re.findall(username):
            this_user = User.objects.get(email=username).username
            user = auth.authenticate(username=this_user, password=password)
        else:
            user = auth.authenticate(username=username, password=password)

        if user is not None:
            token = Token.objects.get(user=user)
            return Response({'token': token.key, 'keyError': 0})
        else:
            return Response({'message': 'no user with such credentials', 'keyError': 1})


@api_view(['POST', 'GET'])
def like(request):
    if request.method == 'GET':
        try:
            like = Like.objects.get(project_id=request.GET['pr_id'], author=request.GET['author'])
        except:
            like = None
        likes_count = len(Like.objects.all())
        if like is not None:
            return Response({
                'keyError': 0,
                'like': like.like,
                'likesCount': likes_count
            })
        else:
            return Response({
                'keyError': 1,
                'message': 'the user never likes this project',
                'likesCount': likes_count,
                'like': 0
            })
    if request.method == 'POST':
        if request.POST['key'] == 'add':
            new_like = Like()
            new_like.project_id = request.POST['project_id']
            new_like.author = request.POST['author']
            new_like.like = 1
            new_like.save()
            return Response({'keyError': 0, 'message': 'like added!'})
        else:
            del_like = Like.objects.get(project_id=request.POST['project_id'], author=request.POST['author'])
            del_like.delete()
            return Response({'keyError': 0, 'message': 'like deleted!'})


@api_view(['POST'])
def reg(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(username=request.POST['login'])
        except:
            user = None

        try:
            email = User.objects.get(email=request.POST['email'])
        except:
            email = None

        pattern = r'[a-zA-Z0-9,. ]+$'
        number_re = re.compile(pattern)


        if user is not None:
            return Response({'keyError': 1, 'messages': 'User with this username already exist!'})
        elif request.POST['password'] != request.POST['passwordRep']:
            return Response({'keyError': 2, 'messages': 'Passwords is not equal!'})
        elif request.POST['email'][-10:] == '@gmail.com':
            return Response({'keyError': 3, 'messages': 'Your email is linked to google account, '
                                                        'you can login with Google.'})
        elif email is not None:
            return Response({'keyError': 3, 'messages': 'User with this email already exist!'})
        elif not number_re.findall(request.POST['login']):
            return Response({'keyError': 1, 'messages': 'Login can contain only numbers and letters'})
        else:
            new_user = User()
            new_user.username = request.POST['login']
            new_user.email = request.POST['email']
            new_user.set_password(request.POST['password'])
            new_user.save()
            Token.objects.create(user=new_user)
            return Response({'keyError': 0, 'messages': 'Registered successfully'})


@api_view(['POST'])
def social_reg(request):
    if request.method == 'POST':

        username = request.POST['email'][:request.POST['email'].find('@')]

        try:
            user = User.objects.get(username=username)
        except:
            user = None

        try:
            email = User.objects.get(email=request.POST['email'])
        except:
            email = None

        if email is not None:
            user = User.objects.get(email=request.POST['email'])
            token = Token.objects.get(user=user)
            return Response({'token': token.key, 'keyError': 0})

        elif user is not None:
            i = 1
            while user is not None:
                try:
                    user = User.objects.get(username=username + str(i))
                except:
                    username = username + str(i)
                    user = None
                i = i + 1

            new_user = User()
            new_user.username = username
            new_user.email = request.POST['email']
            new_user.save()
            Token.objects.create(user=new_user)
            token = Token.objects.get(user=new_user)
            return Response({'keyError': 0, 'messages': 'Registered successfully', 'token': token.key})

        else:
            new_user = User()
            new_user.username = username
            new_user.email = request.POST['email']
            new_user.save()
            Token.objects.create(user=new_user)
            token = Token.objects.get(user=new_user)
            return Response({'keyError': 0, 'messages': 'Registered successfully', 'token': token.key})


@api_view(['GET'])
def theme(request):
    if request.method == 'GET':
        themes = Theme.objects.all()
        types = Type.objects.all()

        returnArr = []
        for item in themes:
            returnArr.append({
                'id': item.id,
                'name': item.name
            })

        returnArr2 = []
        for item in types:
            returnArr2.append({
                'id': item.id,
                'name': item.name
            })
        return Response({'themes': returnArr, 'types': returnArr2})
