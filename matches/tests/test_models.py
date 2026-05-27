from django.test import TestCase
from django.contrib.auth.models import User

from matches.models import (
    Swipe,
    LikePost,
    LikeComment,
    BlockedUser
)


class TestMatchModels(TestCase):

    def setUp(self):

        self.user_a = User.objects.create_user(
            username="usera",
            password="testpassword123"
        )

        self.user_b = User.objects.create_user(
            username="userb",
            password="testpassword123"
        )

    def test_swipe_creation(self):

        swipe = Swipe.objects.create(
            from_user=self.user_a,
            to_user=self.user_b,
            action="like"
        )

        self.assertEqual(
            swipe.action,
            "like"
        )

    def test_swipe_string_method(self):

        swipe = Swipe.objects.create(
            from_user=self.user_a,
            to_user=self.user_b,
            action="like"
        )

        self.assertEqual(
            str(swipe),
            "usera like userb"
        )

    def test_like_post_creation(self):

        post = LikePost.objects.create(
            author=self.user_a,
            body="Test post body"
        )

        self.assertEqual(
            post.author,
            self.user_a
        )

    def test_like_post_string_method(self):

        post = LikePost.objects.create(
            author=self.user_a,
            body="Test post body"
        )

        self.assertIn(
            "usera",
            str(post)
        )

    def test_like_comment_creation(self):

        post = LikePost.objects.create(
            author=self.user_a,
            body="Test post body"
        )

        comment = LikeComment.objects.create(
            post=post,
            author=self.user_b,
            body="Test comment"
        )

        self.assertEqual(
            comment.body,
            "Test comment"
        )

    def test_blocked_user_creation(self):

        blocked = BlockedUser.objects.create(
            blocker=self.user_a,
            blocked=self.user_b
        )

        self.assertEqual(
            blocked.blocker,
            self.user_a
        )

        self.assertEqual(
            blocked.blocked,
            self.user_b
        )

    def test_blocked_user_string_method(self):

        blocked = BlockedUser.objects.create(
            blocker=self.user_a,
            blocked=self.user_b
        )

        self.assertEqual(
            str(blocked),
            "usera blocked userb"
        )
