from matches.models import Swipe


def users_are_trusted(user_a, user_b):
    user_a_likes_b = Swipe.objects.filter(
        from_user=user_a,
        to_user=user_b,
        action="like",
    ).exists()

    user_b_likes_a = Swipe.objects.filter(
        from_user=user_b,
        to_user=user_a,
        action="like",
    ).exists()

    return (
        user_a_likes_b
        and user_b_likes_a
    )
