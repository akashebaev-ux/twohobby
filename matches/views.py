from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect

from .models import Swipe


@login_required
def swipe_user(request, user_id, action):
    target_user = get_object_or_404(User, id=user_id)

    if request.user != target_user and action in ["like", "pass"]:
        Swipe.objects.update_or_create(
            from_user=request.user,
            to_user=target_user,
            defaults={"action": action}
        )

    return redirect("encounters")