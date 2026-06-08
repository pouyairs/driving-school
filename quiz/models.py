from django.db import models
from django.conf import settings


class QuizCategory(models.Model):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Quiz Category"
        verbose_name_plural = "Quiz Categories"
        ordering = ["parent__name", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"

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
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
    )

    main_category = models.ForeignKey(
        QuizCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_questions",
        limit_choices_to={"parent__isnull": True},
        help_text="Main parent category, e.g. مواد مخدر or هفتاد آزمون اصلی",
    )

    sub_category = models.ForeignKey(
        QuizCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_questions",
        limit_choices_to={"parent__isnull": False},
        help_text="Child category, e.g. هروئین or آزمون 1",
    )

    scenario = models.TextField(blank=True)
    scenario_translation = models.TextField(blank=True)

    section = models.CharField(
        max_length=20,
        choices=SECTION_CHOICES,
        default=SECTION_BASIC,
    )

    title = models.TextField()

    title_translation = models.TextField(
        blank=True,
        help_text="Persian translation of the question",
    )

    image = models.ImageField(
        upload_to="quiz/images/",
        blank=True,
        null=True,
    )

    video_url = models.URLField(blank=True)

    max_video_replays = models.PositiveSmallIntegerField(
        default=4,
        help_text="Maximum allowed video views before answering",
    )

    option_1 = models.CharField(max_length=255)
    option_1_translation = models.CharField(max_length=255, blank=True)

    option_2 = models.CharField(max_length=255)
    option_2_translation = models.CharField(max_length=255, blank=True)

    option_3 = models.CharField(max_length=255)
    option_3_translation = models.CharField(max_length=255, blank=True)

    option_4 = models.CharField(max_length=255, blank=True)
    option_4_translation = models.CharField(max_length=255, blank=True)

    correct_answer = models.PositiveSmallIntegerField(
        choices=[
            (1, "گزینه ۱"),
            (2, "گزینه ۲"),
            (3, "گزینه ۳"),
            (4, "گزینه ۴"),
        ]
    )

    correct_answers = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="For multiple correct answers, use comma format: 1,2,4",
    )

    points = models.PositiveSmallIntegerField(
        default=3,
        help_text="Fehlerpunkte / امتیاز خطا",
    )

    explanation = models.TextField(blank=True)

    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["section", "-created_at"]

    def save(self, *args, **kwargs):
        if self.sub_category:
            self.category = self.sub_category
            self.main_category = self.sub_category.parent
        elif self.main_category and not self.category:
            self.category = self.main_category

        super().save(*args, **kwargs)

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

    mode = models.CharField(
        max_length=20,
        choices=[
            ("practice", "Practice"),
            ("read", "Read"),
            ("test", "Test"),
        ],
        default="test",
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

    selected_answers = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Selected answers for multiple choice, e.g. 1,2,4",
    )

    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("exam", "question")

    def __str__(self):
        return f"{self.exam} - {self.question}"


class WrongQuestion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "question")

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"


class FavoriteQuestion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "question")

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"
