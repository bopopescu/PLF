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
            request.session['auth'] = True
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
    #if 'auth' not in request.session:
    #    return login(request)
    context = {}
    context.update(csrf(request))
    items = Item.objects.order_by('id').reverse()
    context['items'] = items

    form = SubmitForm(request.POST, request.FILES)
    context['form'] = form

    if 'auth' not in request.session:
        context['must_log_in'] = True

    # My Items tab
    if 'auth' in request.session:
        # get netid, look up in database, return items
        myitems = Item.objects.filter(student__email__exact=request.session['netid'] + '@princeton.edu')
        context['myitems'] = myitems

    if request.method == 'POST':
        # Login request
        if request.POST.get('login_request'):
            return login(request)

        # Users can't claim items without logging in
        if 'auth' not in request.session:
            return login(request)

        # Resolve items
        if request.POST.get('resolved'):
            getid = request.POST.get('resolved')
            itemlist = Item.objects.filter(id__in = getid)

            if itemlist:
                # remove item
                user = User.objects.filter(email=request.session['netid']+'@princeton.edu')[0]
                user.items.remove(itemlist[0])
                user.save()
                itemlist[0].delete()
            else:
                print "something weird's happening"

            # requery myitems and items
            myitems = Item.objects.filter(student__email__exact=request.session['netid'] + '@princeton.edu')
            context['myitems'] = myitems
            items = Item.objects.order_by('id').reverse()
            context['items'] = items

            return render_to_response('home.html', context)#, context_instance=RequestContext(request))

        # main functionality of submit page
        if request.POST.get('submit_request'):
            if form.is_valid():
                cd = form.cleaned_data
                now = datetime.datetime.now()
                x = False
                if (cd['status'] == 'Lost'):
                    x = True
                em = request.session['netid']+'@princeton.edu'
                print em
                ulist = User.objects.filter(email=em)#[0]
                if not ulist:
                    u = User(email=em)
                    u.save()
                else:
                    u = ulist[0]

                i = Item(status=x, category=cd['category'], desc=cd['desc'], student=u, 
                    sub_date = now, location=cd['location'], picture=cd['picture'],
                    event_date = cd['event_date'], name = cd['name'], claimed=False)
                i.save()
                u.items.add(i)

                context['options'] = 0

                return render_to_response('submit_thanks.html', context)

            else:

                errors = {}
                context['errors'] = errors
                cd = form.cleaned_data
                if not request.POST.get('status', ''):
                    errors['status'] = "Enter a status"
                if not request.POST.get('desc', ''):
                    errors['desc'] = "Enter a description"

                return render_to_response('home.html', context)#, context_instance=RequestContext(request))

        # Claiming an item
        else:
            status = request.POST.get('status')
            em = request.session['netid']+'@princeton.edu'
            if User.objects.filter(email=em):
                u = User.objects.get(email=em)
            else:                # if user not in database 
                u = User(email=em)
                u.save()
            queryuser = request.session['netid'] + '@princeton.edu'
            iden = request.POST.get('identity')
            queryitem = Item.objects.get(id__icontains=iden)
            #queryitem.claimed = True
            #queryitem.save()
            if status == True:
                message = 'Your lost item %s was recently found on the Princeton Lost and Found app by %s. ' % (queryitem.desc, u)
                message += 'Please get in touch with him/her to work out the logistics of returning your item.'
                recipients = [ queryitem.student.email ]
                send_mail('Your Item was Found!', message, 'princetonlostandfound@gmail.com', recipients)
                context['options'] = 1
            else:
                message = 'The item you found (%s) was recently claimed on the Princeton Lost and Found app by %s. ' % (queryitem.desc, u)
                message += 'Please get in touch with him/her to work out the logistics of returning the item.'
                recipients = [ queryitem.student.email ]
                send_mail('An Item You Found was Claimed', message, 'princetonlostandfound@gmail.com', recipients)
                context['options'] = 2

            return render_to_response('submit_thanks.html', context)
    return render_to_response('home.html', context)

def dataReturn(request):
    data = serializers.serialize('json', Item.objects.all(), fields=('status', 'location', 'category', 'desc', 'event_date', 'name'))
    return HttpResponse(data, content_type="application/json")

def myItems(request):
    if 'auth' not in request.session:
        return login(request)
    context = {}
    context.update(csrf(request))

    # get netid, look up in database, return items
    if request.method == 'POST':
        getid = request.POST.get('id')
        item = Item.objects.filter(id__in = getid)[0]

        user = User.objects.filter(email=request.session['netid']+'@princeton.edu')[0]
        user.items.remove(item)
        item.claimed = True
        user.save()
        item.save()

    items = Item.objects.filter(student__email__exact=request.session['netid'] + '@princeton.edu')
    context['items'] = items
    return render_to_response('my_items.html', context)

def submit(request):
    # search bar on left
    if 'auth' not in request.session:
        return login(request)
    items = Item.objects.all()

    # search bar
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            items = Item.objects.filter(category__icontains=q)
            return render_to_response('search_results.html', {'items': items, 'query': q})

    # main functionality of submit page
    if request.method == 'POST':
        form = SubmitForm(request.POST, request.FILES)
        errors = {}

        if form.is_valid():
            cd = form.cleaned_data
            now = datetime.datetime.now()
            x = False
            if (cd['status'] == 'Lost'):
                x = True
            em = request.session['netid']+'@princeton.edu'
            print em
            ulist = User.objects.filter(email=em)#[0]
            if not ulist:
                u = User(email=em)
                u.save()
            if ulist:
                u = ulist[0]

            print u.email
            i = Item(status=x, category=cd['category'], desc=cd['desc'], student=u, 
                sub_date = now, location=cd['location'], picture=cd['picture'],
                event_date = cd['event_date'], claimed=False)
            i.save()
            u.items.add(i)

            context['options'] = 0

            return render_to_response('submit_thanks.html', context)

        else:
            cd = form.cleaned_data
            if not request.POST.get('status', ''):
                errors['status'] = "Enter a status"
            if not request.POST.get('desc', ''):
                errors['desc'] = "Enter a description"
            #if not request.POST.get('netid', ''):
            #    errors['netid'] = "Enter your netid"

            return render_to_response('submit_form.html', {'form': form, 'errors': errors}, context_instance=RequestContext(request))

    else:
        now = datetime.datetime.now()
        datefield = str(now.month) + '/' + str(now.day) + '/' + str(now.year)
        form = SubmitForm(
            initial={'event_date': datefield }
            )
    return render_to_response('submit_form.html', {'form': form}, context_instance=RequestContext(request))



















