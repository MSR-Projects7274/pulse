import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from pulse.departments.models import Department

from .models import Post
from PIL import Image


User = get_user_model()


class FreshUserViewTests(TestCase):
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
