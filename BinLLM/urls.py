from django.urls import path
from . import views


app_name = 'BinLLM'

urlpatterns = [
    # path('', home, name='home'),
    path('', views.index, name='index'),
    path("upload_file", views.upload_file, name='upload_file'),
    path("upload_multi_file", views.upload_multi_file, name='upload_multi_file'),
    path("process_file", views.process_file, name='process_file'),
    path("process_multi_file", views.process_multi_file, name='process_multi_file'),
    path("history", views.history, name='history'),
    path("about", views.about, name='about'),
    path("detailed_file/<str:hash_id>/", views.detailed_file, name='detailed_file'),

    path('delete/<str:hash_id>/',views.file_delete, name='file_delete'),
    path('download/<str:hash_id>/', views.file_download, name='file_download'),
    path('rehandle/<str:hash_id>/', views.file_rehandle, name='file_rehandle')

    # path('list/', views.file_list, name='file_list' ),
    # path('upload/', views.upload_file, name='upload_file' ),
    # path('detail/<int:id>/', views.file_detail, name='file_detail' ),
    #
    # path('error/', views.error, name='error' ),
    #
    # path('download/<int:id>/', views.file_download, name='file_download'),
    # path('delete/<int:id>/',views.file_delete, name='file_delete' ),
    #
    # path('history/', views.recycled_detail, name='recycled_detail'),
]

