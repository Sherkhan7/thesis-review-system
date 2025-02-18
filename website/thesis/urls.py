from django.urls import path

from . import views

app_name = 'thesis'

urlpatterns = [
    path(
        'group/documents/',
        views.DocumentListView.as_view(),
        name='document_list'),
    path(
        'group/create_join/',
        views.GroupCreateJoinView.as_view(),
        name='group_create_join'),
    path(
        'group/create/',
        views.GroupCreateView.as_view(),
        name='group_create'),
    # path(
    #     'group/create/field/<field_id>/teachers/',
    #     views.get_teachers_list_by_field_json,
    #     name='get_teachers'
    # ),
    path(
        'group/join/',
        views.GroupJoinView.as_view(),
        name='group_join'),
    path(
        'group/upload/',
        views.DocumentUploadView.as_view(),
        name='document_upload'),
    path(
        'group/logbooks/create/',
        views.LogbookCreateView.as_view(),
        name='logbook_upload', ),
    path(
        'group/logbooks/<int:pk>/',
        views.LogbookDetailView.as_view(),
        name='logbook_detail', ),
    path(
        'group/invite/',
        views.GroupInviteView.as_view(),
        name='group_invite'),
    path(
        'group/update/',
        views.GroupUpdateView.as_view(),
        name='group_update'),
    path(
        'group/list/',
        views.GroupListView.as_view(),
        name='group_list'),
    path(
        'group/list/<int:batch_number>/',
        views.GroupListView.as_view(),
        name='group_list_batch'),
    path(
        'internal-group/list/',
        views.InternalGroupListView.as_view(),
        name='internal_group_list'),
    path(
        'internal-group/list/<int:batch_number>/',
        views.InternalGroupListView.as_view(),
        name='internal_group_list'),
    path(
        'external-group/list/',
        views.ExternalGroupListView.as_view(),
        name='external_group_list'),
    path(
        'external-group/list/<int:batch_number>/',
        views.ExternalGroupListView.as_view(),
        name='external_group_list'),
    path(
        'group/notifications/',
        views.NotificationListView.as_view(),
        name='user_notifications'),
    path(
        'group/comment/create/',
        views.CommentCreateView.as_view(),
        name='comment_create'
    ),
    path(
        'group/<group_code>/',
        views.DocumentListView.as_view(),
        name='group_detail'),
    path(
        'group/<group_code>/logbooks/<int:pk>/',
        views.LogbookDetailView.as_view(),
        name='logbook_detail'),
    path(
        'group/<group_code>/toggle-logbook/<logbook_id>/',
        views.LogbookApprovedToggleView.as_view(),
        name='toggle-logbook-approval'),
    path(
        'group/<group_code>/toggle-document/<document_id>/',
        views.DocumentAcceptedToggleView.as_view(),
        name='group_document_toggle_view'),
    path(
        'group/<group_code>/comment/create/',
        views.CommentCreateView.as_view(),
        name='comment_create_teacher'
    ),
    path(
        'group/<group_code>/approve/',
        views.StudentGroupApproveView.as_view(),
        name='group_approve'
    ),
    path(
        'group/<group_code>/grading/',
        views.grade_students,
        name='grading_students'
    ),
    path(
        'group/<group_code>/update_progress/',
        views.StudentGroupProgressUpdateView.as_view(),
        name='progress_update'
    ),
]
