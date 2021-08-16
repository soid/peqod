"""catalog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from courses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('deps', views.deps_list, name='departments'),
    path('department/<str:department>', views.department, name='department'),
    path('about', views.about, name='about'),
    path('updates', views.updates, name='updates'),
    path('course/<str:course_code>/<str:term>', views.course, name='course'),
    path('instr/<str:instructor_name>', views.instructor_view, name='instructor'),
]
