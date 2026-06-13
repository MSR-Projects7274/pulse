from django import forms
from .models import Post, Comment


# =========================
# POST FORM
# =========================
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["department", "title", "content", "image"]

        labels = {
            "department": "Channel",
            "title": "Title",
            "content": "Post",
            "image": "Image"
        }


# =========================
# COMMENT FORM
# =========================
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

        widgets = {
            "content": forms.Textarea(attrs={
                "placeholder": "Write a comment...",
                "rows": 3
            })
        }