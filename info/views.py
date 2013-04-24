# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from info.models import Item, User
from info.forms import SubmitForm
import datetime
from django.core.mail import send_mail
from django.core.context_processors import csrf
from django.core import serializers
from django.utils import simplejson
import urllib, re
import _ssl;_ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3


def login(request):
    cas_url = "https://fed.princeton.edu/cas/"
    # URL where the CAS request is coming from
    service_url = 'http://' + urllib.quote(request.META['HTTP_HOST'] + request.META['PATH_INFO'])
    #service_url = 'http://' + 'localhost/'
    service_url = re.sub(r'ticket=[^&]*&?', '', service_url)
    service_url = re.sub(r'\?&?$|&$', '', service_url)
    if "ticket" in request.GET:
        # Validate the ticket
        val_url = cas_url + "validate?service=" + service_url + '&ticket=' + urllib.quote(request.GET['ticket'])
        r = urllib.urlopen(val_url).readlines() # returns 2 lines
        if len(r) == 2 and re.match("yes", r[0]) != None:
            # Set netid for this session. Must have sessions enabled in settings.py
            request.session['netid'] = r[1].strip() 
            # Redirect to homepage
            return HttpResponseRedirect("/home/")
        else:
            # Fraudulent ticket
            return HttpResponse("Failed!")
    else:
        # Go to CAS login page to authenticate
        service_url = re.sub(r'127.0.0.1', 'localhost', service_url)
        # above line to make work on localhost
        login_url = cas_url + 'login?service=' + service_url
        return HttpResponseRedirect(login_url)


def home(request):
#    C = CASClient.CASClient()
#    netid = C.Authenticate()
    context = {}
    context.update(csrf(request))
    error = False
    errors = []
    items = Item.objects.order_by('id').reverse()
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            items = Item.objects.filter(category__icontains=q)
            return render_to_response('search_results.html', {'items': items, 'query': q})

    # This statement handles sending an email
    if request.method == 'POST':
        status = request.POST.get('status')
        queryuser = request.POST.get('email')
        iden = request.POST.get('identity')
        queryitem = Item.objects.filter(id__icontains=iden)[0]
        queryitem.claimed = True
        queryitem.save()
        if status == True:
            message = 'Your lost item %s was recently found on the Princeton Lost and Found app by %s. ' % (queryitem.desc, queryuser)
            message += 'Please get in touch with him/her to work out the logistics of returning your item.'
            recipients = [ queryitem.student.email ]
            send_mail('Your Item was Found!', message, 'princetonlostandfound@gmail.com', recipients)
        else:
            message = 'The item you found (%s) was recently claimed on the Princeton Lost and Found app by %s. ' % (queryitem.desc, queryuser)
            message += 'Please get in touch with him/her to work out the logistics of returning the item.'
            recipients = [ queryitem.student.email ]
            send_mail('An Item You Found was Claimed', message, 'princetonlostandfound@gmail.com', recipients)

        return render_to_response('submit_thanks.html', context)

    context['items'] = items
    context['error'] = error
    return render_to_response('home.html', context)

def dataReturn(request):
    data = serializers.serialize('json', Item.objects.all(), fields=('location', 'category', 'desc'))
    return HttpResponse(data, content_type="application/json")

def myItems(request):
    return HttpResponse()

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

            i = Item(status=x, category=cd['category'], desc=cd['desc'], student=u, 
                sub_date = now, location=cd['location'], picture=cd['picture'],
                event_date = cd['event_date'], claimed=False)
            i.save()
            u.items.add(i)
            # if (user not known)

            return render_to_response('submit_thanks.html')
    else:
        now = datetime.datetime.now()
        datefield = str(now.month) + '/' + str(now.day) + '/' + str(now.year)
        form = SubmitForm(
            initial={'event_date': datefield }
            )
    return render_to_response('submit_form.html', {'form': form}, context_instance=RequestContext(request))



















