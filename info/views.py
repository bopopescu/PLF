# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from info.models import Item, User
from info.forms import SubmitForm
import datetime

def home(request):
    error = False

    # search bar on left
    items = Item.objects.all()
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            items = Item.objects.filter(category__icontains=q)
            return render_to_response('search_results.html', {'items': items, 'query': q})
    
    return render_to_response('home.html', {'items' : items, 'error': error})

def submit(request):
    # search bar on left
    items = Item.objects.all()
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            items = Item.objects.filter(category__icontains=q)
            return render_to_response('search_results.html', {'items': items, 'query': q})

    # main page for submit
    if request.method == 'POST':
        form = SubmitForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            now = datetime.datetime.now()
            x = False
            if (cd['status'] == 'Lost'):
                x = True
            u = User(email=(cd['netid']+'@princeton.edu'))
            u.save()

            i = Item(status=x, category=cd['category'], desc=cd['desc'], student=u, sub_date = now, location=cd['location'])
            i.save()
            u.items.add(i)
            # if (user not known)

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