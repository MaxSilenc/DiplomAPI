from django.urls import path, re_path
from . import views
from .views import UserViewSet
from rest_framework import routers
from django.conf.urls import include

router = routers.DefaultRouter()
router.register('users', UserViewSet)


urlpatterns = [
    path('', views.main),
    path('test', views.test),
    path('auto', views.auto),
    path('login', views.login),
    path('logout', views.logout),
    path('adminPanel', views.adminPanel),
    path('adminPanel/ProjectList/add/', views.adminPanelAddProject),
    path('adminPanel/ProjectList/del/', views.adminPanelDelProject),
    path('adminPanel/ProjectList/', views.adminPanelProjectList),
    path('adminPanel/UsersList/', views.adminPanelUsersList),
    path('adminPanel/UsersList/add/', views.adminPanelAddUser),

    path('projects/<int:pageNumber>/<str:theme_id>/<str:type>/', views.projects),
    re_path(r'^projectPage/(?P<id>[-\w]+)/$', views.projectPage, name='projectPage'),
    path('authUser/', include(router.urls)),
    path('curr/', views.curr_user),
    path('comments/<int:id>/', views.comments),
    path('loginReact/', views.loginReact),
    path('like/', views.like),
    path('reg/', views.reg),
    path('social_reg/', views.social_reg),
    path('themes/', views.theme),
    path('chat/', views.chat),
]