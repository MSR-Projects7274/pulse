from django.db import models
from django.contrib.auth.models import User
from pulse.departments.models import Department
from django.core.validators import RegexValidator
from django.db.models import Sum
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
        return f"{self.user.username} voted {self.value} on post {self.post.id}"


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
