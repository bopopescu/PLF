# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from info.models import Item
from info.forms import SubmitForm

def submit(request):
    if request.method == 'POST':
        form = SubmitForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            i = Item(status=cd['status'], category=cd['category'], desc=cd['desc'], location=cd['location'])
            i.save()
            return HttpResponseRedirect('/submit/thanks')
    else:
        form = SubmitForm()
    return render_to_response('submit_form.html', {'form': form}, context_instance=RequestContext(request))

def submitthanks(request):
    return render_to_response('submit_thanks.html')

def search(request):
    error = False
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            items = Item.objects.filter(category__icontains=q)
            return render_to_response('search_results.html',
                {'items': items, 'query': q})
    return render_to_response('search_form.html', {'error': error})
