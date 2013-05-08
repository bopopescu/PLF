from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from info.models import Item, User
from info.forms import SubmitForm
import datetime
from datetime import date
import time
from datetime import timedelta
from django.core.mail import send_mail
from django.core.context_processors import csrf
from django.core import serializers
from django.utils import simplejson
import urllib, re
import _ssl;_ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3

def cleanCounts(): 
    for user in User.objects.all():
        user.claim_count = 0
        user.submit_count = 0
        user.save()

def thanks(request):
    return HttpResponseRedirect('../')

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
        request.session['netid'] = ''
        request.session['auth'] = False
        # Go to CAS login page to authenticate
        service_url = re.sub(r'127.0.0.1', 'localhost', service_url)
        # above line to make work on localhost
        login_url = cas_url + 'login?service=' + service_url
        return HttpResponseRedirect(login_url)

def logout(request):
    request.session.flush()
    return HttpResponseRedirect('https://fed.princeton.edu/cas/logout')

def home(request):
    # initialize context
    context = {}
    context.update(csrf(request))
    items = Item.objects.order_by('id').reverse()
    context['items'] = items

    if not 'lastDay' in globals():
        global lastDay
        lastDay = date.today()
        #lastTime = time.time()

    # cleanup loop that should run once every three days
    today = date.today()
    if (today - lastDay).days >= 3:
    #if (time.time()-lastTime) > :
        lastDay = today
        #lastTime = time.time()
        cleanCounts()
        #remove items older than 90 days
        for i in items:
            if (today-i.sub_date).days >= 90:        
                # remove item
                user = User.objects.filter(items__id__exact=i.id)[0]
                user.items.remove(i)
                user.save()
                i.delete()

    # should we requery?
    items = Item.objects.order_by('id').reverse()

    if 'options' in request.session:
        context['options'] = request.session['options']
        print "options: " + str(request.session['options'])
        request.session['options'] = 0
    else:
        context['options'] = 0

    form = SubmitForm(request.POST, request.FILES)
    context['form'] = form

    if 'auth' not in request.session or request.session['auth'] is False:
        context['must_log_in'] = True

    # My Items tab
    if 'auth' in request.session and request.session['auth'] is True:
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
            itemlist = Item.objects.filter(id = getid)

            if itemlist:
                # remove item
                user = User.objects.filter(email=request.session['netid']+'@princeton.edu')[0]
                user.items.remove(itemlist[0])
                user.save()
                itemlist[0].delete()

            # requery myitems and items
            #myitems = Item.objects.filter(student__email__exact=request.session['netid'] + '@princeton.edu')
            #context['myitems'] = myitems
            #items = Item.objects.order_by('id').reverse()
            #context['items'] = items

            return HttpResponseRedirect('../thanks')

        # main functionality of submit page
        if request.POST.get('submit_request'):
            em = request.session['netid']+'@princeton.edu'
            ulist = User.objects.filter(email=em)
            if not ulist:
                u = User(email=em)
                u.claim_count = 0
                u.submit_count = 0
                u.save()
            else:
                u = ulist[0]

            # if this user's been submitting too much, redirect back to home with the "sorry" modal popup
            if u.submit_count >= 5:
                context['options'] = 5
                return HttpResponseRedirect('../thanks')

            # if the form's valid...
            elif form.is_valid():
                cd = form.cleaned_data
                now = datetime.datetime.now()
                x = False
                if (cd['status'] == 'Lost'):
                    x = True

                i = Item(status=x, category=cd['category'], desc=cd['desc'], student=u, 
                    sub_date = now, location=cd['location'], picture=cd['picture'],
                    event_date = cd['event_date'], name = cd['name'], claimed=False)
                i.save()
                u.items.add(i)

                request.session['options'] = 1

                #return render_to_response('submit_thanks.html', context)
                return HttpResponseRedirect('../thanks')

            # reload home page and submit modal with error messages
            else:
                errors = {}
                context['errors'] = errors
                cd = form.cleaned_data
                if not request.POST.get('status', ''):
                    errors['status'] = "This field is required"
                if not request.POST.get('desc', ''):
                    errors['desc'] = "This field is required"
                if not request.POST.get('name', ''):
                    errors['name'] = "This field is required"

                return render_to_response('home.html', context)#, context_instance=RequestContext(request))

        # Claiming an item
        else:
            status = request.POST.get('status')
            em = request.session['netid']+'@princeton.edu'
            if User.objects.filter(email=em):
                u = User.objects.get(email=em)
            else:                # if user not in database 
                u = User(email=em)
                u.claim_count = 0
                u.submit_count = 0
                u.save()
            queryuser = request.session['netid'] + '@princeton.edu'
            iden = request.POST.get('identity')
            u.claim_count += 1
            u.save()
            queryitem = Item.objects.get(id=iden)
            #queryitem.claimed = True
            #queryitem.save()
            if (u.claim_count > 3):
                request.session['options'] = 4
            elif status == True:
                message = 'Your lost item %s was recently found on the Princeton Lost and Found app by %s. ' % (queryitem.name, u)
                message += 'Please get in touch with him/her to work out the logistics of returning your item.'
                recipients = [ queryitem.student.email ]
                send_mail('Your Item was Found!', message, 'princetonlostandfound@gmail.com', recipients)
                request.session['options'] = 2
            else:
                message = 'The item you found (%s) was recently claimed on the Princeton Lost and Found app by %s. ' % (queryitem.name, u)
                message += 'Please get in touch with him/her to work out the logistics of returning the item.'
                recipients = [ queryitem.student.email ]
                send_mail('An Item You Found was Claimed', message, 'princetonlostandfound@gmail.com', recipients)
                request.session['options'] = 3
            
            return HttpResponseRedirect('../thanks')
    return render_to_response('home.html', context)

def dataReturn(request):
    data = serializers.serialize('json', Item.objects.all(), fields=('status', 'location', 'category', 'desc', 'event_date', 'name'))
    return HttpResponse(data, content_type="application/json")

def about(request):
    return render_to_response('about.html')

# def myItems(request):
#     if 'auth' not in request.session:
#         return login(request)
#     context = {}
#     context.update(csrf(request))

#     # get netid, look up in database, return items
#     if request.method == 'POST':
#         getid = request.POST.get('id')
#         item = Item.objects.filter(id = getid)[0]

#         user = User.objects.filter(email=request.session['netid']+'@princeton.edu')[0]
#         user.items.remove(item)
#         item.claimed = True
#         user.save()
#         item.save()

#     items = Item.objects.filter(student__email__exact=request.session['netid'] + '@princeton.edu')
#     context['items'] = items
#     return render_to_response('my_items.html', context)

# def submit(request):
#     # search bar on left
#     if 'auth' not in request.session:
#         return login(request)
#     items = Item.objects.all()

#     # search bar
#     if 'q' in request.GET:
#         q = request.GET['q']
#         if not q:
#             error = True
#         else:
#             items = Item.objects.filter(category__icontains=q)
#             return render_to_response('search_results.html', {'items': items, 'query': q})

#     # main functionality of submit page
#     if request.method == 'POST':
#         form = SubmitForm(request.POST, request.FILES)
#         errors = {}

#         if form.is_valid():
#             cd = form.cleaned_data
#             now = datetime.datetime.now()
#             x = False
#             if (cd['status'] == 'Lost'):
#                 x = True
#             em = request.session['netid']+'@princeton.edu'
#             print em
#             ulist = User.objects.filter(email=em)#[0]
#             if not ulist:
#                 u = User(email=em)
#                 u.save()
#             if ulist:
#                 u = ulist[0]

#             print u.email
#             i = Item(status=x, category=cd['category'], desc=cd['desc'], student=u, 
#                 sub_date = now, location=cd['location'], picture=cd['picture'],
#                 event_date = cd['event_date'], claimed=False)
#             i.save()
#             u.items.add(i)

#             context['options'] = 0

#             return render_to_response('submit_thanks.html', context)

#         else:
#             cd = form.cleaned_data
#             if not request.POST.get('status', ''):
#                 errors['status'] = "Enter a status"
#             if not request.POST.get('desc', ''):
#                 errors['desc'] = "Enter a description"
#             #if not request.POST.get('netid', ''):
#             #    errors['netid'] = "Enter your netid"

#             return render_to_response('submit_form.html', {'form': form, 'errors': errors}, context_instance=RequestContext(request))

#     else:
#         now = datetime.datetime.now()
#         datefield = str(now.month) + '/' + str(now.day) + '/' + str(now.year)
#         form = SubmitForm(
#             initial={'event_date': datefield }
#             )
#     return render_to_response('submit_form.html', {'form': form}, context_instance=RequestContext(request))