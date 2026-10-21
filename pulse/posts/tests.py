import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from pulse.departments.models import Department

from .models import Comment, CommentVote, Post, PostVote
from PIL import Image


User = get_user_model()


class FreshUserViewTests(TestCase):
    # Fresh-user access and post creation
    def test_fresh_user_can_open_homepage(self):
        user = User.objects.create_user(
            username="freshuser",
            password="TestPass123!",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/home.html")
        self.assertFalse(response.context["posts"].exists())

    def test_fresh_user_can_open_post_detail_without_vote_history(self):
        fresh_user = User.objects.create_user(
            username="freshdetailuser",
            password="TestPass123!",
        )
        author = User.objects.create_user(
            username="postauthor",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=author,
            department=department,
            title="Fresh user test post",
            content="A post for testing fresh-user access.",
        )

        self.client.force_login(fresh_user)

        response = self.client.get(
            reverse("post_detail", args=[post.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/post_detail.html")
        self.assertEqual(response.context["post"], post)
        self.assertIsNone(response.context["user_post_vote"])
        self.assertFalse(post.votes.exists())
        self.assertFalse(post.comments.exists())

    def test_fresh_user_can_create_post(self):
        fresh_user = User.objects.create_user(
            username="freshcreator",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")

        self.client.force_login(fresh_user)

        response = self.client.post(
            reverse("create_post"),
            {
                "department": department.pk,
                "title": "Fresh user created this",
                "content": "Testing post creation from a brand-new account.",
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(
            Post.objects.filter(
                author=fresh_user,
                department=department,
                title="Fresh user created this",
                content="Testing post creation from a brand-new account.",
            ).exists()
        )

        created_post = Post.objects.get(
            title="Fresh user created this"
        )
        self.assertFalse(created_post.image)

    def test_fresh_user_can_create_post_with_image(self):
        fresh_user = User.objects.create_user(
            username="freshimagecreator",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")

        image_buffer = BytesIO()
        Image.new("RGB", (10, 10)).save(
            image_buffer,
            format="PNG",
        )
        uploaded_image = SimpleUploadedFile(
            "test-image.png",
            image_buffer.getvalue(),
            content_type="image/png",
        )

        self.client.force_login(fresh_user)

        with tempfile.TemporaryDirectory() as media_root:
            with self.settings(
                MEDIA_ROOT=media_root,
                STORAGES={
                    "default": {
                        "BACKEND": (
                            "django.core.files.storage."
                            "FileSystemStorage"
                        ),
                    },
                    "staticfiles": {
                        "BACKEND": (
                            "django.contrib.staticfiles.storage."
                            "StaticFilesStorage"
                        ),
                    },
                },
            ):
                response = self.client.post(
                    reverse("create_post"),
                    {
                        "department": department.pk,
                        "title": "Post with image",
                        "content": "Testing creation with an image.",
                        "image": uploaded_image,
                    },
                )

                self.assertRedirects(
                    response,
                    reverse("home"),
                )

                created_post = Post.objects.get(
                    title="Post with image"
                )

                self.assertEqual(
                    created_post.author,
                    fresh_user,
                )
                self.assertTrue(created_post.image)
                self.assertTrue(
                    created_post.image.name.startswith(
                        "post_images/"
                    )
                )

    # Post editing, deletion and ownership permissions
    def test_post_edit_preserves_and_replaces_image(self):
        user = User.objects.create_user(
            username="posteditor",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")

        initial_buffer = BytesIO()
        Image.new("RGB", (10, 10)).save(
            initial_buffer,
            format="PNG",
        )
        initial_image = SimpleUploadedFile(
            "original-image.png",
            initial_buffer.getvalue(),
            content_type="image/png",
        )

        replacement_buffer = BytesIO()
        Image.new("RGB", (10, 10)).save(
            replacement_buffer,
            format="PNG",
        )
        replacement_image = SimpleUploadedFile(
            "replacement-image.png",
            replacement_buffer.getvalue(),
            content_type="image/png",
        )

        self.client.force_login(user)

        with tempfile.TemporaryDirectory() as media_root:
            with self.settings(
                MEDIA_ROOT=media_root,
                STORAGES={
                    "default": {
                        "BACKEND": (
                            "django.core.files.storage."
                            "FileSystemStorage"
                        ),
                    },
                    "staticfiles": {
                        "BACKEND": (
                            "django.contrib.staticfiles.storage."
                            "StaticFilesStorage"
                        ),
                    },
                },
            ):
                post = Post.objects.create(
                    author=user,
                    department=department,
                    title="Original title",
                    content="Original content.",
                    image=initial_image,
                )

                original_image_name = post.image.name
                original_storage = post.image.storage

                self.assertTrue(
                    original_storage.exists(
                        original_image_name
                    )
                )

                response = self.client.post(
                    reverse("edit_post", args=[post.pk]),
                    {
                        "department": department.pk,
                        "title": "Edited title",
                        "content": "Edited content.",
                    },
                )

                self.assertRedirects(
                    response,
                    reverse("post_detail", args=[post.pk]),
                )

                post.refresh_from_db()

                self.assertEqual(post.title, "Edited title")
                self.assertEqual(post.content, "Edited content.")
                self.assertEqual(
                    post.image.name,
                    original_image_name,
                )
                self.assertTrue(post.is_edited)
                self.assertEqual(post.author, user)
                self.assertTrue(
                    original_storage.exists(
                        original_image_name
                    )
                )

                with self.captureOnCommitCallbacks(execute=True):
                    response = self.client.post(
                        reverse("edit_post", args=[post.pk]),
                        {
                            "department": department.pk,
                            "title": "Edited title again",
                            "content": "Edited again with a new image.",
                            "image": replacement_image,
                        },
                    )

                self.assertRedirects(
                    response,
                    reverse("post_detail", args=[post.pk]),
                )

                post.refresh_from_db()

                self.assertEqual(
                    post.title,
                    "Edited title again",
                )
                self.assertEqual(
                    post.content,
                    "Edited again with a new image.",
                )
                self.assertNotEqual(
                    post.image.name,
                    original_image_name,
                )
                self.assertTrue(
                    post.image.name.startswith(
                        "post_images/"
                    )
                )
                self.assertTrue(
                    post.image.storage.exists(
                        post.image.name
                    )
                )
                self.assertFalse(
                    original_storage.exists(
                        original_image_name
                    )
                )

    def test_post_edit_clears_image_and_deletes_stored_file(self):
        user = User.objects.create_user(
            username="imageclearer",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")

        image_buffer = BytesIO()
        Image.new("RGB", (10, 10)).save(
            image_buffer,
            format="PNG",
        )
        uploaded_image = SimpleUploadedFile(
            "clear-me.png",
            image_buffer.getvalue(),
            content_type="image/png",
        )

        self.client.force_login(user)

        with tempfile.TemporaryDirectory() as media_root:
            with self.settings(
                MEDIA_ROOT=media_root,
                STORAGES={
                    "default": {
                        "BACKEND": (
                            "django.core.files.storage."
                            "FileSystemStorage"
                        ),
                    },
                    "staticfiles": {
                        "BACKEND": (
                            "django.contrib.staticfiles.storage."
                            "StaticFilesStorage"
                        ),
                    },
                },
            ):
                post = Post.objects.create(
                    author=user,
                    department=department,
                    title="Clear image test",
                    content="This image should be cleared.",
                    image=uploaded_image,
                )
                image_name = post.image.name
                storage = post.image.storage

                self.assertTrue(storage.exists(image_name))

                with self.captureOnCommitCallbacks(execute=True):
                    response = self.client.post(
                        reverse("edit_post", args=[post.pk]),
                        {
                            "department": department.pk,
                            "title": "Clear image test",
                            "content": "The image has been cleared.",
                            "image-clear": "on",
                        },
                    )

                self.assertRedirects(
                    response,
                    reverse("post_detail", args=[post.pk]),
                )

                post.refresh_from_db()

                self.assertFalse(post.image)
                self.assertTrue(post.is_edited)
                self.assertFalse(storage.exists(image_name))

    def test_post_delete_removes_stored_image(self):
        user = User.objects.create_user(
            username="imagedeleter",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")

        image_buffer = BytesIO()
        Image.new("RGB", (10, 10)).save(
            image_buffer,
            format="PNG",
        )
        uploaded_image = SimpleUploadedFile(
            "delete-me.png",
            image_buffer.getvalue(),
            content_type="image/png",
        )

        self.client.force_login(user)

        with tempfile.TemporaryDirectory() as media_root:
            with self.settings(
                MEDIA_ROOT=media_root,
                STORAGES={
                    "default": {
                        "BACKEND": (
                            "django.core.files.storage."
                            "FileSystemStorage"
                        ),
                    },
                    "staticfiles": {
                        "BACKEND": (
                            "django.contrib.staticfiles.storage."
                            "StaticFilesStorage"
                        ),
                    },
                },
            ):
                post = Post.objects.create(
                    author=user,
                    department=department,
                    title="Delete image test",
                    content="This post and image should be deleted.",
                    image=uploaded_image,
                )
                post_pk = post.pk
                image_name = post.image.name
                storage = post.image.storage

                self.assertTrue(storage.exists(image_name))

                with self.captureOnCommitCallbacks(execute=True):
                    response = self.client.post(
                        reverse("delete_post", args=[post_pk])
                    )

                self.assertRedirects(response, reverse("home"))
                self.assertFalse(
                    Post.objects.filter(pk=post_pk).exists()
                )
                self.assertFalse(storage.exists(image_name))

    def test_author_delete_cascade_removes_post_image(self):
        user = User.objects.create_user(
            username="cascadeimagedeleter",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")

        image_buffer = BytesIO()
        Image.new("RGB", (10, 10)).save(
            image_buffer,
            format="PNG",
        )
        uploaded_image = SimpleUploadedFile(
            "cascade-delete.png",
            image_buffer.getvalue(),
            content_type="image/png",
        )

        with tempfile.TemporaryDirectory() as media_root:
            with self.settings(
                MEDIA_ROOT=media_root,
                STORAGES={
                    "default": {
                        "BACKEND": (
                            "django.core.files.storage."
                            "FileSystemStorage"
                        ),
                    },
                    "staticfiles": {
                        "BACKEND": (
                            "django.contrib.staticfiles.storage."
                            "StaticFilesStorage"
                        ),
                    },
                },
            ):
                post = Post.objects.create(
                    author=user,
                    department=department,
                    title="Cascade image test",
                    content="Cascade deletion should remove this image.",
                    image=uploaded_image,
                )
                post_pk = post.pk
                image_name = post.image.name
                storage = post.image.storage

                self.assertTrue(storage.exists(image_name))

                with self.captureOnCommitCallbacks(execute=True):
                    user.delete()

                self.assertFalse(
                    Post.objects.filter(pk=post_pk).exists()
                )
                self.assertFalse(storage.exists(image_name))

    def test_post_can_be_deleted(self):
        user = User.objects.create_user(
            username="postdeleter",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=user,
            department=department,
            title="Delete me",
            content="This post should be deleted.",
        )
        post_pk = post.pk

        self.client.force_login(user)

        response = self.client.post(
            reverse("delete_post", args=[post_pk])
        )

        self.assertRedirects(response, reverse("home"))
        self.assertFalse(
            Post.objects.filter(pk=post_pk).exists()
        )

    def test_post_edit_permissions_for_owner_and_non_owner(self):
        owner = User.objects.create_user(
            username="editowner",
            password="TestPass123!",
        )
        non_owner = User.objects.create_user(
            username="editnonowner",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=owner,
            department=department,
            title="Owner post",
            content="Original content.",
        )

        self.client.force_login(owner)

        owner_response = self.client.get(
            reverse("edit_post", args=[post.pk])
        )

        self.assertEqual(owner_response.status_code, 200)

        self.client.force_login(non_owner)

        non_owner_response = self.client.post(
            reverse("edit_post", args=[post.pk]),
            {
                "department": department.pk,
                "title": "Unauthorized edit",
                "content": "This should not be saved.",
            },
        )

        self.assertEqual(non_owner_response.status_code, 403)

        post.refresh_from_db()

        self.assertEqual(post.title, "Owner post")
        self.assertEqual(post.content, "Original content.")
        self.assertFalse(post.is_edited)

    def test_post_delete_permissions_for_owner_and_non_owner(self):
        owner = User.objects.create_user(
            username="deleteowner",
            password="TestPass123!",
        )
        non_owner = User.objects.create_user(
            username="deletenonowner",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=owner,
            department=department,
            title="Protected post",
            content="Only the owner can delete this.",
        )

        self.client.force_login(owner)

        owner_response = self.client.get(
            reverse("delete_post", args=[post.pk])
        )

        self.assertEqual(owner_response.status_code, 200)

        self.client.force_login(non_owner)

        non_owner_response = self.client.post(
            reverse("delete_post", args=[post.pk])
        )

        self.assertEqual(non_owner_response.status_code, 403)
        self.assertTrue(
            Post.objects.filter(pk=post.pk).exists()
        )

    def test_nonexistent_post_returns_404(self):
        response = self.client.get(
            reverse("post_detail", args=[999999])
        )

        self.assertEqual(response.status_code, 404)

    # Comment creation, validation and ownership permissions
    def test_authenticated_user_can_create_comment(self):
        user = User.objects.create_user(
            username="commentcreator",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=user,
            department=department,
            title="Comment test post",
            content="A post waiting for a comment.",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("post_detail", args=[post.pk]),
            {
                "content": "This is a test comment.",
            },
        )

        self.assertRedirects(
            response,
            reverse("post_detail", args=[post.pk]),
        )

        comment = Comment.objects.get(
            content="This is a test comment."
        )

        self.assertEqual(comment.author, user)
        self.assertEqual(comment.post, post)
        self.assertFalse(comment.is_edited)

    def test_expired_session_comment_post_preserves_login_next(self):
        user = User.objects.create_user(
            username="expiredcommenter",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=user,
            department=department,
            title="Expired session comment test",
            content="A post waiting for a comment.",
        )

        detail_url = reverse(
            "post_detail",
            args=[post.pk],
        )

        self.client.force_login(user)

        # Simulate the authenticated session disappearing before submission.
        self.client.logout()

        response = self.client.post(
            detail_url,
            {
                "content": "This comment should not be saved.",
            },
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={detail_url}",
            fetch_redirect_response=False,
        )

        self.assertFalse(
            Comment.objects.filter(
                content="This comment should not be saved."
            ).exists()
        )

    def test_blank_comment_is_rejected(self):
        user = User.objects.create_user(
            username="blankcommenter",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=user,
            department=department,
            title="Blank comment test",
            content="Testing blank comment validation.",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("post_detail", args=[post.pk]),
            {
                "content": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "posts/post_detail.html",
        )
        self.assertTrue(
            response.context["form"].errors.get("content")
        )
        self.assertFalse(
            Comment.objects.filter(post=post).exists()
        )

    def test_whitespace_only_comment_is_rejected(self):
        user = User.objects.create_user(
            username="whitespacecommenter",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=user,
            department=department,
            title="Whitespace comment test",
            content="Testing whitespace comment validation.",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("post_detail", args=[post.pk]),
            {
                "content": "   ",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "posts/post_detail.html",
        )
        self.assertTrue(
            response.context["form"].errors.get("content")
        )
        self.assertFalse(
            Comment.objects.filter(post=post).exists()
        )

    def test_comment_edit_permissions_for_owner_and_non_owner(self):
        owner = User.objects.create_user(
            username="commenteditowner",
            password="TestPass123!",
        )
        non_owner = User.objects.create_user(
            username="commenteditnonowner",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=owner,
            department=department,
            title="Comment edit permission test",
            content="Testing comment ownership.",
        )
        comment = Comment.objects.create(
            post=post,
            author=owner,
            content="Original comment.",
        )

        self.client.force_login(non_owner)

        non_owner_response = self.client.post(
            reverse("edit_comment", args=[comment.pk]),
            {
                "content": "Unauthorized edit.",
            },
        )

        self.assertEqual(non_owner_response.status_code, 403)

        comment.refresh_from_db()

        self.assertEqual(comment.content, "Original comment.")
        self.assertFalse(comment.is_edited)

        self.client.force_login(owner)

        owner_response = self.client.post(
            reverse("edit_comment", args=[comment.pk]),
            {
                "content": "Owner edited this comment.",
            },
        )

        self.assertRedirects(
            owner_response,
            reverse("post_detail", args=[post.pk]),
        )

        comment.refresh_from_db()

        self.assertEqual(
            comment.content,
            "Owner edited this comment.",
        )
        self.assertTrue(comment.is_edited)
        self.assertEqual(comment.author, owner)
        self.assertEqual(comment.post, post)

    def test_comment_delete_permissions_for_owner_and_non_owner(self):
        owner = User.objects.create_user(
            username="commentdeleteowner",
            password="TestPass123!",
        )
        non_owner = User.objects.create_user(
            username="commentdeletenonowner",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=owner,
            department=department,
            title="Comment delete permission test",
            content="Testing comment deletion ownership.",
        )
        comment = Comment.objects.create(
            post=post,
            author=owner,
            content="Protected comment.",
        )

        self.client.force_login(non_owner)

        non_owner_response = self.client.post(
            reverse("delete_comment", args=[comment.pk])
        )

        self.assertEqual(non_owner_response.status_code, 403)
        self.assertTrue(
            Comment.objects.filter(pk=comment.pk).exists()
        )

        self.client.force_login(owner)

        owner_response = self.client.post(
            reverse("delete_comment", args=[comment.pk])
        )

        self.assertRedirects(
            owner_response,
            reverse("post_detail", args=[post.pk]),
        )
        self.assertFalse(
            Comment.objects.filter(pk=comment.pk).exists()
        )

    # Post and comment voting behaviour
    def test_post_vote_upvote_downvote_switch_and_remove(self):
        user = User.objects.create_user(
            username="postvoter",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=user,
            department=department,
            title="Post vote test",
            content="Testing the post voting state machine.",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("post_upvote", args=[post.pk])
        )

        self.assertEqual(response.status_code, 302)

        vote = PostVote.objects.get(
            post=post,
            user=user,
        )

        self.assertEqual(vote.value, 1)
        self.assertEqual(post.score, 1)

        response = self.client.post(
            reverse("post_upvote", args=[post.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PostVote.objects.filter(
                post=post,
                user=user,
            ).exists()
        )
        self.assertEqual(post.score, 0)

        response = self.client.post(
            reverse("post_downvote", args=[post.pk])
        )

        self.assertEqual(response.status_code, 302)

        vote = PostVote.objects.get(
            post=post,
            user=user,
        )
        vote_pk = vote.pk

        self.assertEqual(vote.value, -1)
        self.assertEqual(post.score, -1)

        response = self.client.post(
            reverse("post_upvote", args=[post.pk])
        )

        self.assertEqual(response.status_code, 302)

        vote.refresh_from_db()

        self.assertEqual(vote.pk, vote_pk)
        self.assertEqual(vote.value, 1)
        self.assertEqual(post.score, 1)
        self.assertEqual(
            PostVote.objects.filter(
                post=post,
                user=user,
            ).count(),
            1,
        )

        response = self.client.post(
            reverse("post_upvote", args=[post.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            PostVote.objects.filter(
                post=post,
                user=user,
            ).exists()
        )
        self.assertEqual(post.score, 0)

        # Anonymous vote controls should lead to login, not POST-only URLs.
        self.client.logout()

        home_url = reverse("home")
        login_url = reverse("login")

        response = self.client.get(home_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'action="{login_url}"',
            count=2,
        )
        self.assertContains(
            response,
            f'name="next" value="{home_url}"',
            count=2,
        )
        self.assertNotContains(
            response,
            f'action="{reverse("post_upvote", args=[post.pk])}"',
        )
        self.assertNotContains(
            response,
            f'action="{reverse("post_downvote", args=[post.pk])}"',
        )

    def test_comment_vote_upvote_downvote_switch_and_remove(self):
        user = User.objects.create_user(
            username="commentvoter",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=user,
            department=department,
            title="Comment vote test",
            content="Testing comment voting.",
        )
        comment = Comment.objects.create(
            post=post,
            author=user,
            content="Vote on this comment.",
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("comment_upvote", args=[comment.pk])
        )

        self.assertEqual(response.status_code, 302)

        vote = CommentVote.objects.get(
            comment=comment,
            user=user,
        )

        self.assertEqual(vote.value, 1)
        self.assertEqual(comment.score, 1)

        response = self.client.post(
            reverse("comment_upvote", args=[comment.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            CommentVote.objects.filter(
                comment=comment,
                user=user,
            ).exists()
        )
        self.assertEqual(comment.score, 0)

        response = self.client.post(
            reverse("comment_downvote", args=[comment.pk])
        )

        self.assertEqual(response.status_code, 302)

        vote = CommentVote.objects.get(
            comment=comment,
            user=user,
        )
        vote_pk = vote.pk

        self.assertEqual(vote.value, -1)
        self.assertEqual(comment.score, -1)

        response = self.client.post(
            reverse("comment_upvote", args=[comment.pk])
        )

        self.assertEqual(response.status_code, 302)

        vote.refresh_from_db()

        self.assertEqual(vote.pk, vote_pk)
        self.assertEqual(vote.value, 1)
        self.assertEqual(comment.score, 1)
        self.assertEqual(
            CommentVote.objects.filter(
                comment=comment,
                user=user,
            ).count(),
            1,
        )

        response = self.client.post(
            reverse("comment_upvote", args=[comment.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            CommentVote.objects.filter(
                comment=comment,
                user=user,
            ).exists()
        )
        self.assertEqual(comment.score, 0)

        # Anonymous post/comment actions should return through login safely.
        self.client.logout()

        detail_url = reverse("post_detail", args=[post.pk])
        login_url = reverse("login")

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'action="{login_url}"',
            count=4,
        )
        self.assertContains(
            response,
            f'name="next" value="{detail_url}"',
            count=4,
        )
        self.assertContains(
            response,
            f'href="{login_url}?next=',
            count=1,
        )
        self.assertNotContains(
            response,
            f'action="{reverse("post_upvote", args=[post.pk])}"',
        )
        self.assertNotContains(
            response,
            f'action="{reverse("post_downvote", args=[post.pk])}"',
        )
        self.assertNotContains(
            response,
            f'action="{reverse("comment_upvote", args=[comment.pk])}"',
        )
        self.assertNotContains(
            response,
            f'action="{reverse("comment_downvote", args=[comment.pk])}"',
        )

    # Database constraints protecting valid vote values
    def test_post_vote_rejects_value_outside_allowed_range(self):
        user = User.objects.create_user(
            username="invalidpostvoter",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=user,
            department=department,
            title="Invalid post vote test",
            content="Testing the post vote database constraint.",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PostVote.objects.create(
                    post=post,
                    user=user,
                    value=0,
                )

        self.assertFalse(
            PostVote.objects.filter(
                post=post,
                user=user,
            ).exists()
        )

    def test_comment_vote_rejects_value_outside_allowed_range(self):
        user = User.objects.create_user(
            username="invalidcommentvoter",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=user,
            department=department,
            title="Invalid comment vote test",
            content="Testing the comment vote database constraint.",
        )
        comment = Comment.objects.create(
            post=post,
            author=user,
            content="Invalid vote target.",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CommentVote.objects.create(
                    comment=comment,
                    user=user,
                    value=42,
                )

        self.assertFalse(
            CommentVote.objects.filter(
                comment=comment,
                user=user,
            ).exists()
        )

    # Department filtering and community-page behaviour
    def test_community_page_displays_its_posts(self):
        user = User.objects.create_user(
            username="communityposter",
            password="TestPass123!",
        )
        general = Department.objects.get(name="General")
        development = Department.objects.get(name="Development")

        first_post = Post.objects.create(
            author=user,
            department=general,
            title="First General post",
            content="First community test post.",
        )
        second_post = Post.objects.create(
            author=user,
            department=general,
            title="Second General post",
            content="Second community test post.",
        )
        other_post = Post.objects.create(
            author=user,
            department=development,
            title="Development-only post",
            content="This belongs to another community.",
        )

        response = self.client.get(
            reverse(
                "department_posts",
                args=[general.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "posts/home.html",
        )
        self.assertEqual(
            response.context["current_department"],
            general,
        )

        posts = list(response.context["posts"])

        self.assertEqual(len(posts), 2)
        self.assertIn(first_post, posts)
        self.assertIn(second_post, posts)
        self.assertNotIn(other_post, posts)

        self.assertContains(response, first_post.title)
        self.assertContains(response, second_post.title)
        self.assertNotContains(response, other_post.title)

    def test_empty_community_page_displays_normally(self):
        user = User.objects.create_user(
            username="othercommunityposter",
            password="TestPass123!",
        )
        general = Department.objects.get(name="General")
        announcements = Department.objects.get(name="Announcements")

        other_post = Post.objects.create(
            author=user,
            department=general,
            title="General-only post",
            content="This must not appear in the empty community.",
        )

        response = self.client.get(
            reverse(
                "department_posts",
                args=[announcements.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "posts/home.html",
        )
        self.assertEqual(
            response.context["current_department"],
            announcements,
        )
        self.assertFalse(
            response.context["posts"].exists()
        )

        self.assertContains(response, announcements.name)
        self.assertNotContains(response, other_post.title)

    def test_invalid_community_id_returns_404(self):
        highest_department = Department.objects.order_by("-pk").first()
        invalid_id = highest_department.pk + 1000

        response = self.client.get(
            reverse(
                "department_posts",
                args=[invalid_id],
            )
        )

        self.assertEqual(response.status_code, 404)

    # Profile and custom error-page behaviour
    def test_profile_with_zero_posts_and_comments(self):
        user = User.objects.create_user(
            username="emptyprofile",
            password="TestPass123!",
        )

        response = self.client.get(
            reverse(
                "user_profile",
                args=[user.username],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "posts/profile.html",
        )
        self.assertEqual(
            response.context["profile_user"],
            user,
        )
        self.assertFalse(
            response.context["posts"].exists()
        )
        self.assertFalse(
            response.context["comments"].exists()
        )

        self.assertContains(response, user.username)
        self.assertContains(response, "Posts: 0")
        self.assertContains(response, "Comments: 0")
        self.assertContains(response, "No posts yet.")

    @override_settings(DEBUG=False)
    def test_custom_404_template_is_rendered(self):
        response = self.client.get(
            "/this-page-does-not-exist/"
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(
            response,
            "404.html",
        )
        self.assertContains(
            response,
            "That page drifted out of range.",
            status_code=404,
        )
        self.assertContains(
            response,
            "Back to Pulse",
            status_code=404,
        )

    @override_settings(DEBUG=False)
    def test_permission_failure_renders_custom_403(self):
        owner = User.objects.create_user(
            username="permissionowner",
            password="TestPass123!",
        )
        non_owner = User.objects.create_user(
            username="permissionnonowner",
            password="TestPass123!",
        )
        department = Department.objects.get(name="General")
        post = Post.objects.create(
            author=owner,
            department=department,
            title="Protected permission test",
            content="Only the owner should edit this.",
        )

        self.client.force_login(non_owner)

        response = self.client.get(
            reverse("edit_post", args=[post.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(
            response,
            "403.html",
        )
        self.assertContains(
            response,
            "This one isn't yours to change.",
            status_code=403,
        )
        self.assertContains(
            response,
            "Back to Pulse",
            status_code=403,
        )

    # Search across posts and communities
    def test_search_finds_posts_and_communities(self):
        user = User.objects.create_user(
            username="searchtester",
            password="TestPass123!",
        )
        general = Department.objects.get(name="General")
        development = Department.objects.get(name="Development")

        title_post = Post.objects.create(
            author=user,
            department=general,
            title="Nebula project update",
            content="A normal body without the content search term.",
        )
        content_post = Post.objects.create(
            author=user,
            department=development,
            title="Ordinary development post",
            content="This post contains the unique quasar keyword.",
        )

        title_response = self.client.get(
            reverse("search_communities"),
            {"q": "Nebula"},
        )

        self.assertEqual(title_response.status_code, 200)
        self.assertTemplateUsed(
            title_response,
            "posts/community_search.html",
        )
        self.assertIn(
            title_post,
            title_response.context["posts"],
        )
        self.assertNotIn(
            content_post,
            title_response.context["posts"],
        )

        content_response = self.client.get(
            reverse("search_communities"),
            {"q": "quasar"},
        )

        self.assertIn(
            content_post,
            content_response.context["posts"],
        )
        self.assertNotIn(
            title_post,
            content_response.context["posts"],
        )

        community_response = self.client.get(
            reverse("search_communities"),
            {"q": "General"},
        )

        self.assertIn(
            general,
            community_response.context["departments"],
        )
        self.assertNotIn(
            development,
            community_response.context["departments"],
        )
