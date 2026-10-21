from functools import partial

from django.db import models, transaction
from django.contrib.auth.models import User
from pulse.departments.models import Department
from django.core.validators import RegexValidator
from django.db.models import Sum
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from pulse.posts.validators import validate_image_size

non_whitespace_validator = RegexValidator(
    regex=r"\S",
    message="This field cannot contain only whitespace.",
)


# =========================
# POST (core content)
# =========================
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    title = models.CharField(
        max_length=200,
        validators=[non_whitespace_validator],
    )
    content = models.TextField(
        validators=[non_whitespace_validator],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    image = models.ImageField(
        upload_to="post_images/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"]
            ),
            validate_image_size,
        ],
    )

    def __str__(self):
        return self.title

    # Post score (sum of votes)
    @property
    def score(self):
        return self.votes.aggregate(
            total=Sum("value")
        )["total"] or 0


# =========================
# COMMENT (belongs to Post)
# =========================
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(
        validators=[non_whitespace_validator],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author.username} on {self.post.title}"

    # Comment score (sum of votes)
    @property
    def score(self):
        return self.votes.aggregate(
            total=Sum("value")
        )["total"] or 0


# =========================
# POST VOTES (up/down)
# =========================
class PostVote(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="votes"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    value = models.SmallIntegerField(
        choices=[
            (-1, "Downvote"),
            (1, "Upvote"),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(value=-1) | models.Q(value=1),
                name="postvote_value_valid",
            ),
            models.UniqueConstraint(
                fields=["post", "user"],
                name="unique_post_vote_per_user",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} voted {self.value} "
            f"on post {self.post.id}"
        )


# =========================
# COMMENT VOTES (up/down)
# =========================
class CommentVote(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="votes"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    value = models.SmallIntegerField(
        choices=[
            (-1, "Downvote"),
            (1, "Upvote"),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(value=-1) | models.Q(value=1),
                name="commentvote_value_valid",
            ),
            models.UniqueConstraint(
                fields=["comment", "user"],
                name="unique_comment_vote_per_user",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} voted "
            f"{self.value} on comment {self.comment.id}"
        )


# =========================
# POST IMAGE LIFECYCLE
# =========================
@receiver(pre_save, sender=Post)
def remember_previous_post_image(sender, instance, using, **kwargs):
    if kwargs.get("raw") or not instance.pk:
        return

    update_fields = kwargs.get("update_fields")
    if update_fields is not None and "image" not in update_fields:
        return

    try:
        previous = (
            sender.objects.using(using)
            .only("image")
            .get(pk=instance.pk)
        )
    except sender.DoesNotExist:
        return

    old_image = previous.image
    new_image = instance.image

    old_name = old_image.name if old_image else ""
    new_name = new_image.name if new_image else ""

    if old_name and old_name != new_name:
        instance._previous_post_image = old_image


@receiver(post_save, sender=Post)
def delete_replaced_post_image(sender, instance, using, **kwargs):
    old_image = getattr(instance, "_previous_post_image", None)
    if not old_image:
        return

    del instance._previous_post_image

    transaction.on_commit(
        partial(old_image.delete, save=False),
        using=using,
    )


@receiver(post_delete, sender=Post)
def delete_removed_post_image(sender, instance, using, **kwargs):
    if not instance.image:
        return

    transaction.on_commit(
        partial(instance.image.delete, save=False),
        using=using,
    )
