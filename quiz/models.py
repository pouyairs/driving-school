from django.db import models
from django.conf import settings


class QuizCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Quiz Category"
        verbose_name_plural = "Quiz Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Question(models.Model):
    SECTION_BASIC = "basic"
    SECTION_CLASS_B = "class_b"

    SECTION_CHOICES = [
        (SECTION_BASIC, "Basic Knowledge"),
        (SECTION_CLASS_B, "Class B"),
    ]

    category = models.ForeignKey(
        QuizCategory,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    section = models.CharField(
        max_length=20,
        choices=SECTION_CHOICES,
        default=SECTION_BASIC,
    )

    title = models.TextField()

    image = models.ImageField(
        upload_to="quiz/images/",
        blank=True,
        null=True,
    )

    video_url = models.URLField(
        blank=True,
    )

    max_video_replays = models.PositiveSmallIntegerField(
        default=4,
        help_text="Maximum allowed video views before answering",
    )

    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    option_4 = models.CharField(max_length=255, blank=True)

    correct_answer = models.PositiveSmallIntegerField(
        choices=[
            (1, "گزینه ۱"),
            (2, "گزینه ۲"),
            (3, "گزینه ۳"),
            (4, "گزینه ۴"),
        ]
    )

    points = models.PositiveSmallIntegerField(
        default=3,
        help_text="Fehlerpunkte / امتیاز خطا",
    )

    explanation = models.TextField(blank=True)

    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["section", "-created_at"]

    def __str__(self):
        return self.title[:80]
class ExamSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_sessions",
    )
    questions = models.ManyToManyField(
        Question,
        related_name="exam_sessions",
        blank=True,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return f"Exam #{self.id} - {self.user.username}"

    def total_error_points(self):
        total = 0

        for answer in self.answers.all():
            if not answer.is_correct:
                total += answer.question.points

        return total


class ExamAnswer(models.Model):
    exam = models.ForeignKey(
        ExamSession,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="exam_answers",
    )
    selected_answer = models.PositiveSmallIntegerField()
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("exam", "question")

    def __str__(self):
        return f"{self.exam} - {self.question}"