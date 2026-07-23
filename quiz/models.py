from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class QuizCategory(models.Model):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("دسته‌بندی والد"),
    )

    name = models.CharField(
        _("نام"),
        max_length=100,
    )

    slug = models.SlugField(
        _("نامک"),
        unique=True,
    )

    class Meta:
        verbose_name = _("دسته‌بندی سؤال")
        verbose_name_plural = _("دسته‌بندی‌های سؤال")
        ordering = ["parent__name", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name


class Question(models.Model):
    SECTION_BASIC = "basic"
    SECTION_CLASS_B = "class_b"

    SECTION_CHOICES = [
        (SECTION_BASIC, _("دانش پایه")),
        (SECTION_CLASS_B, _("کلاس B")),
    ]

    category = models.ForeignKey(
        QuizCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
        verbose_name=_("دسته‌بندی"),
    )

    main_category = models.ForeignKey(
        QuizCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_questions",
        limit_choices_to={"parent__isnull": True},
        verbose_name=_("دسته‌بندی اصلی"),
        help_text=_("دسته‌بندی والد اصلی را انتخاب کنید؛ برای مثال مواد مخدر یا هفتاد آزمون اصلی."),
    )

    sub_category = models.ForeignKey(
        QuizCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_questions",
        limit_choices_to={"parent__isnull": False},
        verbose_name=_("زیرمجموعه"),
        help_text=_("زیرمجموعه را انتخاب کنید؛ برای مثال هروئین یا آزمون ۱."),
    )

    scenario = models.TextField(
        _("سناریو"),
        blank=True,
    )

    scenario_translation = models.TextField(
        _("ترجمه سناریو"),
        blank=True,
    )

    section = models.CharField(
        _("بخش"),
        max_length=20,
        choices=SECTION_CHOICES,
        default=SECTION_BASIC,
    )

    title = models.TextField(
        _("متن سؤال"),
    )

    title_translation = models.TextField(
        _("ترجمه سؤال"),
        blank=True,
        help_text=_("ترجمه فارسی سؤال"),
    )

    image = models.ImageField(
        _("تصویر"),
        upload_to="quiz/images/",
        blank=True,
        null=True,
    )

    video_url = models.URLField(
        _("نشانی ویدیو"),
        blank=True,
    )

    max_video_replays = models.PositiveSmallIntegerField(
        _("حداکثر دفعات پخش ویدیو"),
        default=4,
        help_text=_("حداکثر تعداد دفعات مجاز مشاهده ویدیو پیش از پاسخ‌دادن"),
    )

    option_1 = models.CharField(
        _("گزینه ۱"),
        max_length=255,
    )

    option_1_translation = models.CharField(
        _("ترجمه گزینه ۱"),
        max_length=255,
        blank=True,
    )

    option_2 = models.CharField(
        _("گزینه ۲"),
        max_length=255,
    )

    option_2_translation = models.CharField(
        _("ترجمه گزینه ۲"),
        max_length=255,
        blank=True,
    )

    option_3 = models.CharField(
        _("گزینه ۳"),
        max_length=255,
    )

    option_3_translation = models.CharField(
        _("ترجمه گزینه ۳"),
        max_length=255,
        blank=True,
    )

    option_4 = models.CharField(
        _("گزینه ۴"),
        max_length=255,
        blank=True,
    )

    option_4_translation = models.CharField(
        _("ترجمه گزینه ۴"),
        max_length=255,
        blank=True,
    )

    correct_answer = models.PositiveSmallIntegerField(
        _("پاسخ صحیح"),
        choices=[
            (1, _("گزینه ۱")),
            (2, _("گزینه ۲")),
            (3, _("گزینه ۳")),
            (4, _("گزینه ۴")),
        ],
    )

    correct_answers = models.CharField(
        _("پاسخ‌های صحیح"),
        max_length=20,
        blank=True,
        default="",
        help_text=_("برای چند پاسخ صحیح، شماره‌ها را با ویرگول وارد کنید؛ مانند 1,2,4"),
    )

    points = models.PositiveSmallIntegerField(
        _("امتیاز خطا"),
        default=3,
        help_text=_("Fehlerpunkte / امتیاز خطا"),
    )

    explanation = models.TextField(
        _("توضیح پاسخ"),
        blank=True,
    )

    is_published = models.BooleanField(
        _("منتشر شده"),
        default=True,
    )

    created_at = models.DateTimeField(
        _("زمان ایجاد"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("سؤال")
        verbose_name_plural = _("سؤال‌ها")
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
    MODE_PRACTICE = "practice"
    MODE_READ = "read"
    MODE_TEST = "test"

    MODE_CHOICES = [
        (MODE_PRACTICE, _("تمرین")),
        (MODE_READ, _("مطالعه")),
        (MODE_TEST, _("آزمون")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_sessions",
        verbose_name=_("کاربر"),
    )

    questions = models.ManyToManyField(
        Question,
        related_name="exam_sessions",
        blank=True,
        verbose_name=_("سؤال‌ها"),
    )

    mode = models.CharField(
        _("حالت"),
        max_length=20,
        choices=MODE_CHOICES,
        default=MODE_TEST,
    )

    started_at = models.DateTimeField(
        _("زمان شروع"),
        auto_now_add=True,
    )

    finished_at = models.DateTimeField(
        _("زمان پایان"),
        blank=True,
        null=True,
    )

    is_finished = models.BooleanField(
        _("پایان یافته"),
        default=False,
    )

    class Meta:
        verbose_name = _("جلسه آزمون")
        verbose_name_plural = _("جلسه‌های آزمون")
        ordering = ["-started_at"]

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
        verbose_name=_("آزمون"),
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="exam_answers",
        verbose_name=_("سؤال"),
    )

    selected_answer = models.PositiveSmallIntegerField(
        _("پاسخ انتخاب‌شده"),
    )

    selected_answers = models.CharField(
        _("پاسخ‌های انتخاب‌شده"),
        max_length=20,
        blank=True,
        default="",
        help_text=_("برای چند پاسخ انتخابی، شماره‌ها را با ویرگول وارد کنید؛ مانند 1,2,4"),
    )

    is_correct = models.BooleanField(
        _("صحیح است"),
        default=False,
    )

    answered_at = models.DateTimeField(
        _("زمان پاسخ"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("پاسخ آزمون")
        verbose_name_plural = _("پاسخ‌های آزمون")
        unique_together = ("exam", "question")

    def __str__(self):
        return f"{self.exam} - {self.question}"


class WrongQuestion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("کاربر"),
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_("سؤال"),
    )

    created_at = models.DateTimeField(
        _("زمان ایجاد"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("سؤال اشتباه")
        verbose_name_plural = _("سؤال‌های اشتباه")
        unique_together = ("user", "question")

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"


class FavoriteQuestion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("کاربر"),
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_("سؤال"),
    )

    created_at = models.DateTimeField(
        _("زمان ایجاد"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("سؤال موردعلاقه")
        verbose_name_plural = _("سؤال‌های موردعلاقه")
        unique_together = ("user", "question")

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"
