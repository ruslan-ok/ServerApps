from django.contrib.auth.decorators import login_required, permission_required
from proj.v_dirs import do_dirs
from proj.v_proj import do_proj, do_change_dir


#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# �।�⠢����� ��� �⮡ࠦ���� ᯨ᪠ ���ࠢ�����
def dirs_view(request):
    return do_dirs(request, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# �।�⠢����� ��� ।���஢���� ���ࠢ�����
def dirs_edit(request, pk):
    return do_dirs(request, int(pk))

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# �।�⠢����� ��� �⮡ࠦ���� ᯨ᪠ ����権 �஥��
def proj_view(request):
    return do_proj(request, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# �।�⠢����� ��� ।���஢���� ����樨 �஥��
def proj_edit(request, pk):
    return do_proj(request, int(pk))

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# ��४��祭�� �� ��㣮� ���ࠢ�����
def change_dir(request, pk):
    return do_change_dir(request, int(pk))
