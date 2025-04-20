from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Level(models.Model):
    # 1) define your code values
    ENTRY = 'ENTRY'
    PSU   = 'PSU'
    GOVT  = 'GOVT'
    CAT   = 'CAT'
    UPSC  = 'UPSC'
    ADV   = 'ADV'

    # 2) tie each to its human‑readable label
    LEVEL_CHOICES = [
        (ENTRY, 'Entry Level (Basic IT Jobs, Internships)'),
        (PSU,   'PSU Exams (ONGC, BHEL, SAIL)'),
        (GOVT,  'Government Exams (SSC, Banking)'),
        (CAT,   'MBA Entrance (CAT, XAT)'),
        (UPSC,  'UPSC/State PSC'),
        (ADV,   'Advanced (Olympiads, Research)'),
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
        ('tech',    'Technical Knowledge'),
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
    part_title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Display order (1-based)"
    )
    
    # Core Learning Content
    explanation = models.TextField(
        blank=True,
        help_text="Detailed explanation with LaTeX formulas like $$E=mc^2$$"
    )
    key_formulas = models.TextField(
        blank=True,
        help_text="Important formulas (auto-extracted from explanation)"
    )
    
    # Structured Examples
    examples = models.JSONField(
        default=list,
        help_text="List of examples with structure: ["
                 "{'problem':'...','solution':'...','analysis':'...','complexity':'Beginner/Intermediate/Advanced'}]"
    )
    
    # Learning Aids
    common_pitfalls = models.TextField(
        blank=True,
        help_text="One pitfall per line"
    )
    quick_tricks = models.TextField(
        blank=True,
        help_text="One trick per line"
    )
    practice_advice = models.TextField(blank=True)
    recommended_resources = models.TextField(
        blank=True,
        help_text="One resource per line"
    )
    
    # Metadata
    is_miscellaneous = models.BooleanField(
        default=False,
        help_text="Check if this is a 'catch-all' part"
    )
    last_updated = models.DateTimeField(auto_now=True)
    version = models.PositiveSmallIntegerField(default=1)
    
    class Meta:
        unique_together = ('topic', 'level', 'order')
        ordering = ['order']
        verbose_name = "Tutorial Part"
        verbose_name_plural = "Tutorial Parts"

    def __str__(self):
        return f"{self.topic.name} - {self.level.name} - Part {self.order}: {self.part_title}"

    def save(self, *args, **kwargs):
        """Auto-extract formulas and ensure clean data"""
        if not self.key_formulas and self.explanation:
            self.key_formulas = self.extract_formulas()
        super().save(*args, **kwargs)
    
    def extract_formulas(self):
        """Extract LaTeX formulas from explanation"""
        import re
        formulas = re.findall(r'\$\$(.*?)\$\$', self.explanation, re.DOTALL)
        return '\n'.join(formulas) if formulas else ''