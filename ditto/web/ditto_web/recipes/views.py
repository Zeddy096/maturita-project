from django.shortcuts import get_object_or_404, render
from .models import Recipe

# Create your views here.

def recipe_list(request):
    q = (request.GET.get("q") or "").strip()
    mode = request.GET.get("mode") or "name"    # name | ingredients
    t = (request.GET.get("t") or "").strip()    # minuty
    cmp = request.GET.get("cmp") or "le"        # le | eq

    recipes = Recipe.objects.all().order_by("-id")

    if q:
        if mode == "ingredients":
            recipes = recipes.filter(ingredients__icontains=q)
        else:
            recipes = recipes.filter(name__icontains=q)

    if t.isdigit():
        t_val = int(t)
        if cmp == "eq":
            recipes = recipes.filter(time_min=t_val)
        else:
            recipes = recipes.filter(time_min__lte=t_val)

    context = {"recipes": recipes, "q": q, "mode": mode, "t": t, "cmp": cmp}
    return render(request, "recipes/list.html", context)

def recipe_detail(request, pk):
    recipe = get_object_or_404 (Recipe, pk=pk)
    return render(request, "recipes/detail.html", {"recipe": recipe})

        