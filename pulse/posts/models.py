from django.db import models
from django.contrib.auth.models import User
from pulse.departments.models import Department
from django.db.models import Sum


# =========================
# POST (core content)
# =========================
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image = models.ImageField(
        upload_to="post_images/",
        blank=True,
        null=True
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
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    value = models.SmallIntegerField()  # +1 or -1

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)


    class Meta:
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user.username} voted {self.value} on post {self.post.id}"


# =========================
# COMMENT VOTES (up/down)
# =========================
class CommentVote(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    value = models.SmallIntegerField()  # +1 or -1

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        unique_together = ("comment", "user")

    def __str__(self):
        return f"{self.user.username} voted {self.value} on comment {self.comment.id}"