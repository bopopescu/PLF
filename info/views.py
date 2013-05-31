from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from info.models import Item, User
from info.forms import SubmitForm
import datetime
from datetime import date
import time
from datetime import timedelta
from PIL import Image, ImageOps
from django.core.mail import send_mail
from django.core.context_processors import csrf
from django.core import serializers
from django.utils import simplejson
import urllib, re
import json
import sys, os
import operator
import _ssl;_ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3
from django.core.files.storage import default_storage
from django.conf import settings

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
    if (today - lastDay).days >= 0:
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
                if i.picture.name:
                    default_storage.delete(i.picture.name)
                i.delete()

    # should we requery?
    items = Item.objects.order_by('id').reverse()

    if 'options' in request.session:
        context['options'] = request.session['options']
        #print "options: " + str(request.session['options'])
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
                if itemlist[0].picture.name:
                    default_storage.delete(itemlist[0].picture.name)
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

            valid_date = True
            if request.POST.get('event_date') != '':
                submitted = str(request.POST.get('event_date'))
                realtime = str(datetime.datetime.now())
                subfields = submitted.split('-')
                realfields = realtime.split(' ')[0].split('-')

                for i in range(len(subfields)):
                    if int(subfields[i]) > int(realfields[i]):
                        valid_date = False

            # if this user's been submitting too much, redirect back to home with the "sorry" modal popup
            if u.submit_count >= 5:
                context['options'] = 5
                return HttpResponseRedirect('../thanks')


            # if the form's valid...
            elif form.is_valid() and valid_date:
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
                
                if cd['picture'] is not None:
                    path = os.path.join(settings.MEDIA_ROOT, i.picture.url)
                    thumbnail = Image.open(path)
                    thumbnail = thumbnail.resize((230, 230), Image.ANTIALIAS)
                    thumbnail.save(path)

                request.session['options'] = 1

                #return render_to_response('submit_thanks.html', context)
                return HttpResponseRedirect('../thanks')

            # reload home page and submit modal with error messages
            else:
                errors = {}
                context['errors'] = errors
                cd = form.cleaned_data
                if not 'event_date' in cd or valid_date is False:
                    errors['event_date'] = "Invalid date"
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
            elif status == True: # means it's a lost item
                message = 'Your lost item (%s) was recently found on the Princeton Lost and Found app by %s. ' % (queryitem.name, u)
                message += 'Please get in touch with him/her to work out the logistics of returning your item.'
                recipients = [ queryitem.student.email ]
                send_mail('Your Lost Item was Found!', message, 'princetonlostandfound@gmail.com', recipients)
                request.session['options'] = 2
            else:
                message = 'The item you found (%s) was recently claimed on the Princeton Lost and Found app by %s. ' % (queryitem.name, u)
                message += 'Please get in touch with him/her to work out the logistics of returning the item.'
                recipients = [ str(queryitem.student.email) ]
                send_mail('An Item You Found was Claimed', message, 'princetonlostandfound@gmail.com', recipients)

                message = 'The item you claimed (%s) was posted by user %s. ' % (queryitem.name, queryitem.student.email)
                message += 'Please get in touch with him/her to work out the logistics of returning the item.'
                recipients = [ em ]
                send_mail('You Claimed an Item', message, 'princetonlostandfound@gmail.com', recipients)
                
                request.session['options'] = 3
            
            return HttpResponseRedirect('../thanks')
    return render_to_response('home.html', context)

def search(request):
    searchval = request.GET['val']
    terms = searchval.split(' ')
    matches = {}
    for item in Item.objects.all():
        count = 0
        for t in terms:
            if item.location.lower().find(t.lower()) != -1:
                count += 1
            if item.desc.lower().find(t.lower()) != -1:
                count += 1
            if item.name.lower().find(t.lower()) != -1:
                count += 1
            if item.category.lower() == t.lower():
                count += 1
        if count > 0:
            matches[item.id] = count

    sorted_matches = sorted(matches.iteritems(), key=operator.itemgetter(1), reverse=True)
    idList = []
    for i in sorted_matches:
        idList.append(i[0])
        print i[1]
    queryset = Item.objects.filter(id__in=idList)
    data = serializers.serialize('json', queryset, fields=('status', 'location', 'category', 'desc', 'event_date', 'name', 'picture'))
    return HttpResponse(data, content_type="application/json")

def advSearch(request):
    searchval = request.GET['val']
    aspects = searchval.split(',')
    location = aspects[0]
    name = aspects[1]
    category = aspects[2]
    date = aspects[3]
    desc = aspects[4]
    status = aspects[5]
    date_range = aspects[6]

    matches = []

    for item in Item.objects.all():
        if location != 'e.g. Frist' and item.location.lower().find(t.lower()) == -1:
            continue
        if desc != '':
            for d in desc.split('\n'):
                if item.desc.lower().find(d.lower()) == -1:
                    continue
        if status != 'undefined':
            if status == 'found' and item.status == True:
                continue
            elif status == 'lost' and item.status == False:
                continue
        if name != 'e.g. Black North Face Jacket' and item.name.lower().find(name.lower()) == -1:
            continue
        if category != 'Any' and category != 'null':
            if item.category.lower() != category:
                continue
        # uh date stuff goes here :p
        matches.append(item.id)

    queryset = Item.objects.filter(id__in=matches)
    data = serializers.serialize('json', queryset, fields=('status', 'location', 'category', 'desc', 'event_date', 'name', 'picture'))
    return HttpResponse(data, content_type="application/json")

def default(request):
    recentIDs = []
    recent_items = Item.objects.all()
    num_items = len(recent_items)
    for i in range(5):
        try:
            recentIDs.append(recent_items[num_items-i].id)
        except:
            pass
    queryset = Item.objects.filter(id__in=recentIDs)
    data = serializers.serialize('json', queryset, fields=('status', 'location', 'category', 'desc', 'event_date', 'name', 'picture'))
    return HttpResponse(data, content_type="application/json")

