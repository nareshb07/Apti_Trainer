from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Level(models.Model):

    LEVEL_CHOICES = [
        ('Basic', 'Campus placements, internships'),
        ('Intermediate' , 'Banking, SSC, GRE'),
        ('Advance',  'CAT, XAT, IT company hard tests'),
        ('Specialized Sections' , '(DI, Puzzles, Logical Reasoning)'),
    ]

    name = models.CharField(
        max_length=50,
        choices=LEVEL_CHOICES,
        unique=True,
    )
    slug = models.SlugField(max_length=50, unique=True)

    # use validators to force this into the 1–6 range
    difficulty_order = models.PositiveSmallIntegerField(
        unique=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(len(LEVEL_CHOICES))
        ]
    )

    class Meta:
        ordering = ['difficulty_order']

    def __str__(self):
        # show the friendly label rather than the code
        return self.get_name_display()

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    # (optional) a fixed set of categories
    CATEGORY_CHOICES = [
        ('quant',   'Quantitative Aptitude'),
        ('verbal',  'Verbal Ability'),
        ('logical', 'Logical Reasoning'),
        # ('tech',    'Technical Knowledge'),
    ]
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        blank=True,
    )

    description = models.TextField(blank=True)
    prerequisite_topics = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='is_prerequisite_for',
    )

    # ← new! link to Level
    levels = models.ManyToManyField(
        'Level',
        blank=True,
        related_name='topics',
        help_text='Which exam levels this topic belongs to'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class TutorialPart(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tutorial_parts')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='tutorial_parts')

    part_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)

    key_concepts = models.TextField(help_text="Explain the important concepts covered")
    preparation_strategy = models.TextField(blank=True, help_text="Optional: how to prepare for this part")
    example_problems = models.TextField(help_text="Include solved examples with step-by-step explanations")
    explanations = models.TextField(help_text="Explain concepts or patterns in detail")
    common_pitfalls = models.TextField(blank=True, help_text="Mention commonly made mistakes")
    order = models.PositiveSmallIntegerField(
        default=1,
        help_text="Display order within the topic-level combination"
    )
    is_complete = models.BooleanField(
        default=False,
        help_text="Mark as complete for comprehensive tutorials"
    )
    quick_tips = models.TextField(
        blank=True,
        help_text="Shortcuts and memory aids",
        # Changed from quick_tricks to quick_tips
    )

    prerequisite_parts = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='is_prerequisite_for',
        help_text="Select parts that should be learned before this one."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('topic', 'level', 'part_name')
        ordering = ['topic', 'level', 'part_name']

    def __str__(self):
        return f"{self.part_name} - {self.topic.name} ({self.level.name})"


