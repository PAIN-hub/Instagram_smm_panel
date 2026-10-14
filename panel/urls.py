from django.urls import path
from panel import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Accounts
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('accounts/delete/<int:account_id>/', views.delete_account, name='delete_account'),
    path('accounts/export/', views.export_accounts_csv, name='export_accounts_csv'),
    path('accounts/trigger-create/', views.trigger_create_account_task, name='trigger_create_account_task'),
    
    # Proxies
    path('proxies/', views.proxies_list, name='proxies_list'),
    path('proxies/delete/<int:proxy_id>/', views.delete_proxy, name='delete_proxy'),
    path('proxies/scrape/', views.trigger_scrape_proxies, name='trigger_scrape_proxies'),
    path('proxies/test/', views.trigger_test_proxies, name='trigger_test_proxies'),
    path('proxies/test/<int:proxy_id>/', views.test_single_proxy, name='test_single_proxy'),
    
    # Targets
    path('targets/', views.targets_list, name='targets_list'),
    path('targets/delete/<int:target_id>/', views.delete_target, name='delete_target'),
    
    # Tasks
    path('tasks/', views.tasks_list, name='tasks_list'),
    path('tasks/cancel/<int:task_id>/', views.cancel_task, name='cancel_task'),
    path('tasks/clear/', views.clear_tasks, name='clear_tasks'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/logs/', views.get_task_logs, name='get_task_logs'),
    
    # Settings
    path('settings/', views.settings_view, name='settings_view'),
]
