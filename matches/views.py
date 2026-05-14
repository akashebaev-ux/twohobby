from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from .forms import LikePostForm, LikeCommentForm
from .models import Swipe, LikePost


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


@login_required
def likes(request):
    liked_users = Swipe.objects.filter(
        from_user=request.user,
        action="like"
    ).select_related("to_user")

    liked_user_ids = liked_users.values_list(
        "to_user",
        flat=True
    )

    posts = LikePost.objects.filter(
        author__id__in=list(liked_user_ids) + [request.user.id]
    )

    can_post = liked_users.exists()

    form = LikePostForm()
    comment_form = LikeCommentForm()

    if request.method == "POST" and can_post:

        if "comment_submit" in request.POST:

            comment_form = LikeCommentForm(request.POST)

            if comment_form.is_valid():

                post = get_object_or_404(
                    LikePost,
                    id=request.POST.get("post_id")
                )

                comment = comment_form.save(commit=False)

                comment.author = request.user
                comment.post = post

                comment.save()

                return redirect("likes")

        else:

            form = LikePostForm(request.POST)

            if form.is_valid():

                post = form.save(commit=False)

                post.author = request.user

                post.save()

                return redirect("likes")

    return render(request, "matches/likes.html", {
        "liked_users": liked_users,
        "posts": posts,
        "form": form,
        "comment_form": comment_form,
        "can_post": can_post,
    })


@login_required
def toggle_like_post(request, post_id):
    post = get_object_or_404(LikePost, id=post_id)

    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user)
    else:
        post.liked_by.add(request.user)

    return redirect("likes")