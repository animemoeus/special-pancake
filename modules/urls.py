from django.urls import path

from modules.views import ModuleActionView
from modules.views import ModuleListView

urlpatterns = [
    path("", ModuleListView.as_view(), name="module-list"),
    path("<int:module_id>/action/", ModuleActionView.as_view(), name="module-action"),
]

app_name = "modules"
