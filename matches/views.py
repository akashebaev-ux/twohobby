"""Views for swiping, likes, posts, comments, sharing, and blocking."""


from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from chat.models import ChatRoom, ChatMessage
from .forms import LikePostForm, LikeCommentForm
from .models import Swipe, LikePost, BlockedUser


@login_required
def swipe_user(request, user_id, action):
    """Save a user's swipe action and redirect to encounters."""

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
    """Display liked users, related posts, and handle post comments."""

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
    """Add or remove the current user's like on a post."""

    post = get_object_or_404(LikePost, id=post_id)

    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user)
    else:
        post.liked_by.add(request.user)

    return redirect("likes")


@login_required
def delete_like_post(request, post_id):
    """Delete a like post owned by the current user."""

    post = get_object_or_404(
        LikePost,
        id=post_id,
        author=request.user
    )

    if request.method == "POST":
        post.delete()

    return redirect("likes")


@login_required
def share_like_post(request, post_id):
    """Share a like post into a private chat room."""

    post = get_object_or_404(LikePost, id=post_id)

    existing_room = ChatRoom.objects.filter(
        users=request.user
    ).filter(
        users=post.author
    ).first()

    if existing_room:
        room = existing_room
    else:
        room = ChatRoom.objects.create()
        room.users.add(request.user, post.author)

    ChatMessage.objects.create(
        room=room,
        sender=request.user,
        message=f"Shared post: {post.body}"
    )

    return redirect("room", room_id=room.id)


@login_required
def block_user(request, user_id):
    """Block a user and redirect back to the profile list."""

    blocked_user = get_object_or_404(User, id=user_id)

    if request.user != blocked_user:
        BlockedUser.objects.get_or_create(
            blocker=request.user,
            blocked=blocked_user
        )

    return redirect("profile_list")


@login_required
def unblock_user(request, user_id):
    """Unblock a user and redirect back to the chat room."""

    blocked_user = get_object_or_404(User, id=user_id)

    BlockedUser.objects.filter(
        blocker=request.user,
        blocked=blocked_user
    ).delete()

    return redirect("room", room_id=request.GET.get("room"))
