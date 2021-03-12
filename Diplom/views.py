from django.shortcuts import render, redirect
from Diplom.models import Projects, Comments, Like, Theme, Type, Message, Chat, ProjectInWork
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
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.views import APIView
from rest_framework import serializers


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





















@api_view(['GET', 'POST', 'PUT'])
def projects(request, pageNumber, theme_id, type):

    if request.method == 'GET':
        if request.GET['inWork'] == '0':
            if request.GET['search'] == '':
                if theme_id == 'all' and type == 'all':
                    all_items = Projects.objects.filter(in_work=False)
                elif theme_id == 'all' and type != 'all':
                    all_items = Projects.objects.filter(type=type, in_work=False)
                elif theme_id != 'all' and type == 'all':
                    all_items = Projects.objects.filter(theme_id=theme_id, in_work=False)
                else:
                    all_items = Projects.objects.filter(theme_id=theme_id, type=type, in_work=False)
            else:
                if theme_id == 'all' and type == 'all':
                    all_items = Projects.objects.filter(Q(headline_name__icontains=request.GET['search']) |
                                                        Q(text__icontains=request.GET['search']), in_work=False)
                elif theme_id == 'all' and type != 'all':
                    all_items = Projects.objects.filter(Q(type=type) &
                                                        (Q(headline_name__icontains=request.GET['search']) |
                                                         Q(text__icontains=request.GET['search'])), in_work=False)
                elif theme_id != 'all' and type == 'all':
                    all_items = Projects.objects.filter(Q(theme_id=theme_id) &
                                                        (Q(headline_name__icontains=request.GET['search']) |
                                                         Q(text__icontains=request.GET['search'])), in_work=False)
                else:
                    all_items = Projects.objects.filter(Q(theme_id=theme_id) & Q(type=type) &
                                                        (Q(headline_name__icontains=request.GET['search']) |
                                                         Q(text__icontains=request.GET['search'])), in_work=False)
        else:
            if theme_id == 'all' and type == 'all':
                all_items = Projects.objects.filter(Q(headline_name__icontains=request.GET['search']) |
                                                    Q(text__icontains=request.GET['search']))
            elif theme_id == 'all' and type != 'all':
                all_items = Projects.objects.filter(Q(type=type) &
                                                    (Q(headline_name__icontains=request.GET['search']) |
                                                     Q(text__icontains=request.GET['search'])))
            elif theme_id != 'all' and type == 'all':
                all_items = Projects.objects.filter(Q(theme_id=theme_id) &
                                                    (Q(headline_name__icontains=request.GET['search']) |
                                                     Q(text__icontains=request.GET['search'])))
            else:
                all_items = Projects.objects.filter(Q(theme_id=theme_id) & Q(type=type) &
                                                    (Q(headline_name__icontains=request.GET['search']) |
                                                     Q(text__icontains=request.GET['search'])))

        page = pageNumber
        projects_paginator = Paginator(all_items, 4)

        if page == 0:
            projects = Projects.objects.all()
        else:
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
                'img2': item.img2.url,
                'img3': item.img3.url,
                'name': item.name,
                'work': item.in_work,
            })

        project = {
            "items": returnArr,
            "page": page,
            "count": len(all_items)
        }
        return Response(project)

    parser_classes = (MultiPartParser, FormParser)
    if request.method == 'POST':

        try:
            some_name = Projects.objects.get(headline_name=request.POST['headline_name'])
        except:
            some_name = None

        try:
            some_theme = Theme.objects.get(name=request.POST['theme_id'])
        except:
            some_theme = None

        try:
            some_type = Type.objects.get(name=request.POST['type'])
        except:
            some_type = None

        try:
            some_file = Projects.objects.get(name=request.POST['name'])
        except:
            some_file = None


        if some_name is not None:
            return Response({'keyError': 1, 'message': 'Project with this headline name already exist!'})
        if some_theme is None:
            return Response({'keyError': 2, 'message': 'No such themes, you need to add new theme with this name!'})
        if some_type is None:
            return Response({'keyError': 3, 'message': 'No such type, you need to add new type with this name!'})
        if some_file is not None:
            return Response({'keyError': 4, 'message': 'Project with this file name already exist!'})


        new_project = Projects()
        new_project.headline_name = request.POST['headline_name']
        new_project.name = request.POST['name']
        new_project.img = FileSystemStorage().save('img/' + request.FILES['img'].name, request.FILES['img'])
        new_project.img2 = FileSystemStorage().save('img/' + request.FILES['img2'].name, request.FILES['img2'])
        new_project.img3 = FileSystemStorage().save('img/' + request.FILES['img3'].name, request.FILES['img3'])
        new_project.text = request.POST['text']
        new_project.theme_id = request.POST['theme_id']
        new_project.type = request.POST['type']
        if request.POST['in_work'] == '0':
            new_project.in_work = False
        else:
            new_project.in_work = True

        myfile = request.FILES.getlist('project')
        fs = FileSystemStorage()
        for item in myfile:
            filename = fs.save('Ue4Project/' + request.POST['name'] + '/' + item.name, item)
        fs.delete(myfile[-1].name)
        new_project.save()

        if new_project.in_work == True:
            new_project_in_work = ProjectInWork()
            new_project_in_work.project_id = new_project.id
            try:
                user = User.objects.get(username=request.POST['username'])
            except:
                user = None
            if user is not None:
                new_project_in_work.user_id = user.id
                new_project_in_work.save()
            else:
                return Response({'keyError': 5, 'message': 'No users with such username'})

        return Response({'keyError': 0, 'message': 'Nice!', 'project': {

                'id': new_project.id,
                'title': new_project.headline_name,
                'text': new_project.text,
                'directLink': 'theme1',
                'img': new_project.img.url,
                'img2': new_project.img2.url,
                'img3': new_project.img3.url,
                'name': new_project.name,
                'work': new_project.in_work

        }})

    if request.method == 'PUT':
        if request.POST['whatToDo'] == 'delete':
            project = Projects.objects.get(id=request.POST['id'])
            comments = Comments.objects.filter(project_id=request.POST['id'])
            likes = Like.objects.filter(project_id=request.POST['id'])
            project_in_work = ProjectInWork.objects.filter(project_id=request.POST['id'])
            for item in project_in_work:
                item.delete()
            for item in likes:
                item.delete()
            for item in comments:
                item.delete()

            project.delete()
            FileSystemStorage().delete('img/' + project.img.url[11:])
            FileSystemStorage().delete('img/' + project.img2.url[11:])
            FileSystemStorage().delete('img/' + project.img3.url[11:])

            arr_files = FileSystemStorage().listdir('Ue4Project/' + project.name + '/')[1]
            for item in arr_files:
                FileSystemStorage().delete('Ue4Project/' + project.name + '/' + item)

            FileSystemStorage().delete('Ue4Project/' + project.name)
            return Response({'keyError': 0, 'message': 'Nice!'})
        if request.POST['whatToDo'] == 'update':

            update_project = Projects.objects.get(id=request.POST['id'])

            try:
                some_name = Projects.objects.get(headline_name=request.POST['headline_name'])
            except:
                some_name = None

            try:
                some_theme = Theme.objects.get(name=request.POST['theme_id'])
            except:
                some_theme = None

            try:
                some_type = Type.objects.get(name=request.POST['type'])
            except:
                some_type = None

            try:
                some_file = Projects.objects.get(name=request.POST['name'])
            except:
                some_file = None

            if (some_name is not None) and (update_project.headline_name != some_name.headline_name):
                return Response({'keyError': 1, 'message': 'Project with this headline name already exist!'})
            if some_theme is None:
                return Response({'keyError': 2, 'message': 'No such themes, you need to add new theme with this name!'})
            if some_type is None:
                return Response({'keyError': 3, 'message': 'No such type, you need to add new type with this name!'})
            if (some_file is not None) and (update_project.name != some_file.name):
                return Response({'keyError': 4, 'message': 'Project with this file name already exist!'})

            update_project.headline_name = request.POST['headline_name']
            update_project.name = request.POST['name']
            try:
                img = request.POST['img']
            except:
                img = None

            try:
                img2 = request.POST['img2']
            except:
                img2 = None

            try:
                img3 = request.POST['img3']
            except:
                img3 = None

            if img is None:
                FileSystemStorage().delete('img/' + update_project.img.url[11:])
                update_project.img = FileSystemStorage().save('img/' + request.FILES['img'].name, request.FILES['img'])

            if img2 is None:
                FileSystemStorage().delete('img/' + update_project.img2.url[11:])
                update_project.img2 = FileSystemStorage().save('img/' + request.FILES['img2'].name, request.FILES['img2'])

            if img3 is None:
                FileSystemStorage().delete('img/' + update_project.img3.url[11:])
                update_project.img3 = FileSystemStorage().save('img/' + request.FILES['img3'].name, request.FILES['img3'])


            update_project.text = request.POST['text']
            update_project.theme_id = request.POST['theme_id']
            update_project.type = request.POST['type']
            if request.POST['in_work'] == '0':
                update_project.in_work = False
                try:
                    project_in_work = ProjectInWork.objects.get(project_id=update_project.id)
                except:
                    project_in_work = None

                if project_in_work is not None:
                    project_in_work.delete()
            else:
                if update_project.in_work == True:
                    update_project.in_work = True
                else:
                    try:
                        user = User.objects.get(username=request.POST['username'])
                    except:
                        user = None

                    if user is None:
                        return Response({'keyError': 5, 'message': 'No such users with this name!'})
                    else:
                        new_project_in_work = ProjectInWork()
                        new_project_in_work.user_id = user.id
                        new_project_in_work.project_id = update_project.id
                        new_project_in_work.save()
                        update_project.in_work = True

            try:
                newProj = request.POST['project']
            except:
                newProj = None

            if newProj is None:
                arr_files = FileSystemStorage().listdir('Ue4Project/' + update_project.name + '/')[1]
                for item in arr_files:
                    FileSystemStorage().delete('Ue4Project/' + update_project.name + '/' + item)
                FileSystemStorage().delete('Ue4Project/' + update_project.name)

                myfile = request.FILES.getlist('project')
                fs = FileSystemStorage()
                for item in myfile:
                    filename = fs.save('Ue4Project/' + request.POST['name'] + '/' + item.name, item)
                fs.delete(myfile[-1].name)

            update_project.save()
            return Response({
                'update': True
            })



@api_view(['GET'])
def projectPage(request, id):
    project = Projects.objects.get(id=id)
    username = ''
    if project.in_work == True:
        username = User.objects.get(id=ProjectInWork.objects.get(project_id=id).user_id).username

    projectJson = {
        'id': project.id,
        'title': project.headline_name,
        'text': project.text,
        'directLink': 'theme1',
        'img': project.img.url,
        'img2': project.img2.url,
        'img3': project.img3.url,
        'name': project.name,
        'work': project.in_work,
        'theme': project.theme_id,
        'type': project.type,
        'username': username,
    }
    return Response(projectJson)


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
                'userId': token.user.id,
                'name': token.user.first_name,
                'lastName': token.user.last_name,
                'status': token.user.is_staff,
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

        page = request.GET.get('page')
        projects_paginator = Paginator(all_items, 10)

        try:
            comm = projects_paginator.page(page)
        except PageNotAnInteger:
            comm = projects_paginator.page(1)
        except EmptyPage:
            comm = projects_paginator.page(projects_paginator.num_pages)

        justTest = 0

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
            'count': len(all_items)
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
        likes_count = len(Like.objects.filter(project_id=request.GET['pr_id']))
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


@api_view(['POST', 'PUT'])
def reg(request):

    if request.method == 'POST':
        try:
            key = request.POST['key']
        except:
            key = None

        if key is not None:
            if Token.objects.get(key=request.POST['key']).user.is_staff == True:

                all_users = User.objects.all()

                return_arr = []

                for item in all_users:
                    return_arr.append({
                        'login': item.username,
                        'email': item.email,
                        'userId': item.id,
                        'name': item.first_name,
                        'lastName': item.last_name,
                        'status': item.is_staff,
                    })

                return Response({'keyError': 0, 'messages': 'Nice!', 'users': return_arr})

            else:
                Response({'keyError': 1, 'messages': 'You are bad dude!'})


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
            new_user.first_name = request.POST['name']
            new_user.last_name = request.POST['lastName']
            new_user.email = request.POST['email']
            new_user.set_password(request.POST['password'])

            if request.POST['status'] == '1':
                new_user.is_staff = True

            new_user.save()
            Token.objects.create(user=new_user)
            return Response({'keyError': 0, 'messages': 'Registered successfully'})

    if request.method == 'PUT':
        if request.POST['whatToDo'] == 'update':
            try:
                curr_user = User.objects.get(id=request.POST['id'])
            except:
                curr_user = None

            if curr_user is not None:
                if request.POST['login'] != '':
                    try:
                        user = User.objects.get(username=request.POST['login'])
                    except:
                        user = None

                    if user is not None:
                        if user.id == request.POST['id']:
                            return Response({'keyError': 0, 'messages': 'successfully'})
                        else:
                            return Response({'keyError': 2, 'messages': 'User with this username already exist!'})
                    else:
                        curr_user.username = request.POST['login']
                        curr_user.save()
                if request.POST['email'] != '':
                    try:
                        user = User.objects.get(email=request.POST['email'])
                    except:
                        user = None

                    if user is not None:
                        if user.id == request.POST['id']:
                            return Response({'keyError': 0, 'messages': 'successfully'})
                        else:
                            return Response({'keyError': 3, 'messages': 'User with this email already exist!'})
                    else:
                        curr_user.email = request.POST['email']
                        curr_user.save()
                if request.POST['name'] != '':
                    curr_user.first_name = request.POST['name']
                    curr_user.save()
                if request.POST['lastName'] != '':
                    curr_user.last_name = request.POST['lastName']
                    curr_user.save()
                return Response({'keyError': 0, 'messages': 'successfully'})
            else:
                return Response({'keyError': 1, 'messages': 'No users with this ID!'})
        if request.POST['whatToDo'] == 'delete':
            curr_user = User.objects.get(id=request.POST['id'])
            curr_user.delete()
            return Response({'keyError': 0, 'messages': 'Nice!'})


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


@api_view(['GET', 'POST', 'PUT'])
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

    if request.method == 'POST':
        if request.POST['typesOrThemes'] == 'types':
            try:
                some_type = Type.objects.get(name=request.POST['name'])
            except:
                some_type = None

            if some_type is None:
                newType = Type()
                newType.name = request.POST['name']
                newType.save()
                return Response({'keyError': 0, 'message': 'type', 'new': {
                    'id': newType.id,
                    'name': newType.name,
                }})
            else:
                return Response({'keyError': 1, 'message': 'Type with this name already exist!'})

        if request.POST['typesOrThemes'] == 'themes':
            try:
                some_theme = Theme.objects.get(name=request.POST['name'])
            except:
                some_theme = None

            if some_theme is None:
                newtheme = Theme()
                newtheme.name = request.POST['name']
                newtheme.save()
                return Response({'keyError': 0, 'message': 'theme', 'new': {
                    'id': newtheme.id,
                    'name': newtheme.name,
                }})
            else:
                return Response({'keyError': 2, 'message': 'Theme with this name already exist!'})

    if request.method == 'PUT':
        if request.POST['typesOrThemes'] == 'types':
            updateType = Type.objects.get(id=request.POST['id'])

            if request.POST['newName'] == '':
                updateType.delete()
                return Response({'keyError': 1, 'message': 'type'})
            else:
                updateType.name = request.POST['newName']
                updateType.save()
                return Response({'keyError': 0, 'message': 'type', 'new': {
                    'id': updateType.id,
                    'name': updateType.name,
                }})
        if request.POST['typesOrThemes'] == 'themes':
            updateTheme = Theme.objects.get(id=request.POST['id'])

            if request.POST['newName'] == '':
                updateTheme.delete()
                return Response({'keyError': 1, 'message': 'theme'})
            else:
                updateTheme.name = request.POST['newName']
                updateTheme.save()
                return Response({'keyError': 0, 'message': 'theme', 'new': {
                    'id': updateTheme.id,
                    'name': updateTheme.name,
                }})


@api_view(['GET', 'PUT', 'POST'])
def chat(request):
    if request.method == 'GET':
        try:
            chat = Chat.objects.get(username=request.GET['username'])
        except:
            chat = None

        if chat is not None:
            all_items = Message.objects.filter(chat_id=chat.id)

            returnArr = []

            for item in all_items:
                returnArr.append({
                    'id': item.id,
                    'chat_id': item.chat_id,
                    'text': item.text,
                    'author': item.author
                })

            return Response({'chat': {
                'id': chat.id,
                'username': chat.username,
                'adminname': chat.adminname,
            }, 'messages': returnArr, 'keyError': 0})
        else:
            return Response({'keyError': 1, 'messages': 'no chat for this user'})

    elif request.method == 'PUT':
        old_message = Message.objects.get(id=request.POST['id'])
        old_message.text = request.POST['text']
        if old_message.text == '':
            old_message.delete()
        else:
            old_message.save()
        return Response({'answer': True})

    elif request.method == 'POST':
        if request.POST['chatId'] == 'undefined':
            return Response({'keyError': 2, 'messages': 'something going wrong!'})

        try:
            chat = Chat.objects.get(id=request.POST['chatId'])
        except:
            chat = None

        if chat is None:
            chat = Chat.objects.create(username=request.POST['username'], adminname='None')

        new_message = Message()
        new_message.chat_id = chat.id
        new_message.text = request.POST['text']
        new_message.author = request.POST['username']
        new_message.save()
        return Response({'keyError': 0, 'messages': 'successfully'})


@api_view(['GET'])
def project_in_work(request):
    try:
        projects_in_work = ProjectInWork.objects.filter(user_id=request.GET['user_id'])
    except:
        projects_in_work = None

    if projects_in_work is not None:
        projects_arr = []
        for item in projects_in_work:
            project = Projects.objects.get(id=item.project_id)
            projects_arr.append({
                'id': project.id,
                'title': project.headline_name,
                'text': project.text,
                'directLink': 'theme1',
                'img': project.img.url,
                'img2': project.img2.url,
                'img3': project.img3.url,
                'name': project.name
            })
        return Response({'keyError': 0, 'messages': 'successfully', 'projects': projects_arr})
    else:
        return Response({'keyError': 1, 'messages': 'no projects!'})


@api_view(['GET', 'PUT'])
def empty_chats(request):
    if request.method == 'GET':
        try:
            chats = Chat.objects.filter(adminname=request.GET['adminname'])
        except:
            chats = None

        if chats is not None:
            arr = []
            for item in chats:
                arr.append({
                    'id': item.id,
                    'user': item.username
                })
            return Response({'keyError': 0, 'messages': 'successfully', 'chats': arr})
        else:
            return Response({'keyError': 1, 'messages': 'no such chats!'})
    if request.method == 'PUT':
        chat = Chat.objects.get(id=request.POST['id'])
        chat.adminname = request.POST['adminname']
        chat.save()
        return Response({'keyError': 0, 'messages': 'added admin!'})



