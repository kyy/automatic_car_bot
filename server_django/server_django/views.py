from django.shortcuts import render
from django.http import HttpResponseRedirect


def page_404(request, exception):
    return render(request, "main/404.html", status=404)
