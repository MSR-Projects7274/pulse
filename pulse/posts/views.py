from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Post, Comment, PostVote, CommentVote
from .forms import PostForm, CommentForm
from pulse.departments.models import Department
from django.contrib.auth.models import User
from django.db.models import Sum

# =========================
# HOME (FEED)
# =========================
def home(request):
    posts = Post.objects.all().order_by("-created_at")

    user = request.user

    for post in posts:
        if user.is_authenticated:
            post.user_vote = PostVote.objects.filter(
                post=post,
                user=user
            ).first()
        else:
            post.user_vote = None

    return render(request, "posts/home.html", {
        "posts": posts
    })

# =========================
# COMMUNITY SEARCH
# =========================
def search_communities(request):

    query = request.GET.get("q")

    departments = []

    if query:
        departments = Department.objects.filter(
            name__icontains=query
        )

    return render(
        request,
        "posts/community_search.html",
        {
            "departments": departments,
            "query": query
        }
    )

# =========================
# CREATE POST
# =========================
@login_required
def create_post(request):

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            return redirect("home")

    else:
        form = PostForm()

    return render(request, "posts/create_post.html", {
        "form": form
    })

# =========================
# EDIT POST
# =========================
@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Only the author can edit
    if post.author != request.user:
        return redirect("home")

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )

        if form.is_valid():

            edited_post = form.save(commit=False)

            # Mark as edited
            edited_post.is_edited = True

            edited_post.save()

            return redirect(
                "post_detail",
                pk=post.pk
            )

    else:
        form = PostForm(instance=post)

    return render(
        request,
        "posts/edit_post.html",
        {
            "form": form,
            "post": post
        }
    )

# =========================
# DELETE POST
# =========================
@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Only the author can delete
    if post.author != request.user:
        return redirect("home")

    if request.method == "POST":
        post.delete()

        return redirect("home")

    return render(
        request,
        "posts/delete_post.html",
        {
            "post": post
        }
    )

# =========================
# POST DETAIL + COMMENTS
# =========================
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    user = request.user

    comments = post.comments.all().order_by("-created_at")

    if user.is_authenticated:
        user_post_vote = PostVote.objects.filter(
            post=post,
            user=user
        ).first()
    else:
        user_post_vote = None

    for comment in comments:
        if user.is_authenticated:
            comment.user_vote = CommentVote.objects.filter(
                comment=comment,
                user=user
            ).first()
        else:
            comment.user_vote = None

    if request.method == "POST":

        if not user.is_authenticated:
            return redirect("login")

        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = user
            comment.save()

            return redirect("post_detail", pk=post.pk)

    else:
        form = CommentForm()

    return render(request, "posts/post_detail.html", {
        "post": post,
        "comments": comments,
        "form": form,
        "user_post_vote": user_post_vote,
    })


# =========================
# POST VOTE
# =========================
@login_required
def toggle_post_vote(request, pk, value):
    post = get_object_or_404(Post, pk=pk)

    vote = PostVote.objects.filter(
        post=post,
        user=request.user
    ).first()

    print("======")
    print("USER:", request.user)
    print("VALUE CLICKED:", value)
    print("EXISTING:", vote)

    if vote:
        if vote.value == value:
            print("Deleting existing vote")
            vote.delete()
        else:
            print("Changing vote")
            vote.value = value
            vote.save()
    else:
        print("Creating new vote")
        PostVote.objects.create(
            post=post,
            user=request.user,
            value=value
        )

    print("DB NOW:", PostVote.objects.filter(post=post))

    return redirect(request.META.get("HTTP_REFERER", "home"))

# =========================
# COMMENT VOTE
# =========================
@login_required
def toggle_comment_vote(request, pk, value):
    comment = get_object_or_404(Comment, pk=pk)

    vote = CommentVote.objects.filter(
        comment=comment,
        user=request.user
    ).first()

    if vote:
        if vote.value == value:
            vote.delete()
        else:
            vote.value = value
            vote.save()
    else:
        CommentVote.objects.create(
            comment=comment,
            user=request.user,
            value=value
        )

    return redirect(request.META.get("HTTP_REFERER", "home"))

# =========================
# COMMENT EDIT
# =========================
@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    # Only the author can edit
    if comment.author != request.user:
        return redirect("home")

    if request.method == "POST":
        form = CommentForm(
            request.POST,
            instance=comment
        )

        if form.is_valid():

            edited_comment = form.save(commit=False)

            # Mark as edited
            edited_comment.is_edited = True

            edited_comment.save()

            return redirect(
                "post_detail",
                pk=comment.post.pk
            )

    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "posts/edit_comment.html",
        {
            "form": form,
            "comment": comment
        }
    )

# =========================
# COMMENT DELETION
# =========================
@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    # Only the author can delete
    if comment.author != request.user:
        return redirect("home")

    post_pk = comment.post.pk

    if request.method == "POST":
        comment.delete()
        return redirect(
            "post_detail",
            pk=post_pk
        )

    return render(
        request,
        "posts/delete_comment.html",
        {
            "comment": comment
        }
    )

# =========================
# DEPARTMENT PAGE
# =========================
def department_posts(request, department_id):

    posts = Post.objects.filter(
        department_id=department_id
    ).order_by("-created_at")

    user = request.user

    for post in posts:
        if user.is_authenticated:
            post.user_vote = PostVote.objects.filter(
                post=post,
                user=user
            ).first()
        else:
            post.user_vote = None

    department = posts.first().department if posts.exists() else None

    return render(
    request,
    "posts/home.html",
    {
        "posts": posts,
        "current_department": department
    }
)

# =========================
# USER PROFILE
# =========================
def user_profile(request, username):

    user_profile = get_object_or_404(
        User,
        username=username
    )

    posts = Post.objects.filter(
        author=user_profile
    ).order_by("-created_at")

    comments = Comment.objects.filter(
        author=user_profile
    ).order_by("-created_at")

    return render(
        request,
        "posts/profile.html",
        {
            "profile_user": user_profile,
            "posts": posts,
            "comments": comments,
        }
    )