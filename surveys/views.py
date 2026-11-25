from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from .forms import SurveyForm
from .models import Survey, delete_expired_surveys


def render_board(request, form=None, survey=None, active_dialog=None):
    delete_expired_surveys()
    context = {
        "surveys": Survey.objects.active(),
        "form": form if form is not None else SurveyForm(),
        "survey": survey,
        "active_dialog": active_dialog,
    }
    return render(request, "surveys/board.html", context)


@never_cache
@require_GET
def board(request):
    return render_board(request)


@never_cache
@require_http_methods(["GET", "POST"])
def add_survey(request):
    if request.method == "POST":
        form = SurveyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Survei berhasil ditambahkan.")
            return redirect("board")
    else:
        form = SurveyForm()

    return render_board(request, form=form, active_dialog="add")


@never_cache
@require_GET
def survey_detail(request, pk):
    survey = get_object_or_404(Survey.objects.active(), pk=pk)
    if request.headers.get("X-Survey-Fragment") == "detail":
        return render(request, "surveys/detail.html", {"survey": survey})

    return render_board(request, survey=survey, active_dialog="detail")
