from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from .forms import RequestForm
from .models import Request
from django.views import generic
import uuid
from .tasks import start_task
import pandas as pd


class GetData(generic.FormView):
    template_name = "scrape/index.html"
    form_class = RequestForm

    def form_valid(self, form):
        # uuid生成
        _uuid = str(uuid.uuid4())
        # GCPストレージ
        # 権限は考慮すべき
        gcs_bucket = "gs://scraping_django0083"
        # formオブジェクトの初期化
        f = form.save(commit=False)
        # formにuuidを代入
        f.uuid = _uuid
        task_id = start_task.delay(_uuid)
        print("task_id:", task_id)
        # formを保存
        f.save()
        print("form:", form.cleaned_data)

        context = {
            "url": form.cleaned_data["url"],
            "form": self.form_class,
            "name": f"scrape {datetime.today()}",
            "result": Request.objects.all().order_by("-date")
        }
        return render(
            self.request,
            self.template_name,
            context
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = f"scrape {datetime.today()}"
        context["result"] = Request.objects.all().order_by("-date")
        return context


def downloader(request, uuid):
    gcs_bucket = "gs://scraping_django0083"
    filename = f"{gcs_bucket}/{uuid}.pkl"
    df = pd.read_pickle(filename)

    # テンプレ
    res = HttpResponse(content_type="text/csv; charset=utf-8")
    file_name = f"{datetime.today()}_dj.csv"
    res["Content-Disposition"] = f"attachment; filename*=utf-8\'\'{file_name}"
    df.to_csv(res, index=False)
    return res
