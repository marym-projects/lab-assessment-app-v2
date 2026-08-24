
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from assessments.views import RoleBasedLoginView


urlpatterns = [

    # =====================================================
    # DJANGO ADMIN
    # =====================================================

    path(
        "admin/",
        admin.site.urls,
    ),

    # =====================================================
    # LOGIN
    # =====================================================

    path(
        "login/",
        RoleBasedLoginView.as_view(),
        name="login",
    ),

    # =====================================================
    # LOGOUT
    # =====================================================

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # =====================================================
    # ASSESSMENT SYSTEM
    # =====================================================

    path(
        "",
        include("assessments.urls"),
    ),
]

