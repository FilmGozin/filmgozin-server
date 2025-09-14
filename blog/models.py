from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    class PostType(models.TextChoices):
        MOVIE = 'movie', 'Movie'
        SERIES = 'series', 'Series'
        INTERVIEW = 'interview', 'Interview'
        NEWS = 'news', 'Hollywood News'
        PRODUCTION = 'production', 'Film Production'
        CRITICISM = 'criticism', 'Criticism'
        DOCUMENTARY = 'documentary', 'Documentary'

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='posts')
    thumbnail = models.ImageField(upload_to='blog_thumbnails/', blank=True, null=True)
    post_type = models.CharField(
        max_length=20,
        choices=PostType.choices,
        default=PostType.MOVIE
    )
    content = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
