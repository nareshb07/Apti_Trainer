from django.db import models

class Topic(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} -- {self.category}"


class Level(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TutorialPart(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tutorial_parts')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='tutorial_parts')
    part_title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(help_text="Order in which this part should appear")

    class Meta:
        unique_together = ('topic', 'level', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.topic.name} - {self.level.name} - Part {self.order}: {self.part_title}"
