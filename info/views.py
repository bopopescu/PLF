# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from info.models import Item, User
from info.forms import SubmitForm
import datetime
from django.core.mail import send_mail
from django.core.context_processors import csrf


def home(request):
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

            i = Item(status=x, category=cd['category'], desc=cd['desc'], student=u, sub_date = now, location=cd['location'], picture=cd['picture'])
            i.save()
            u.items.add(i)
            # if (user not known)

            return render_to_response('submit_thanks.html')
    else:
        form = SubmitForm()
    return render_to_response('submit_form.html', {'form': form}, context_instance=RequestContext(request))

#def submitthanks(request):
#    return render_to_response('submit_thanks.html')

#def search(request):
#    print("yooo")
#    context = {}
#    context.update(csrf(request))
#    error = False
#    if 'q' in request.GET:
#        q = request.GET['q']
#        if not q:
#            error = True
#        else:
#            items = Item.objects.filter(category__icontains=q)
#            context['items'] = items
#            context['query'] = q
#            return render_to_response('search_results.html', context)

    # This statement handles sending an email
#    if request.method == 'POST':
#        founduser = request.POST.get('email')
#        iden = request.POST.get('identity')
#        founditem = Item.objects.filter(id__icontains=iden)[0]
#        message = 'Your lost item %s was recently found on the Princeton Lost and Found app by %s. ' % (founditem.desc, founduser)
#        message += 'Please get in touch with him/her to work out the logistics of returning your item.'
#        recipients = [ founditem.student.email ]
#        send_mail('Your Item was Found!', message, 'tortorareed@hotmail.com', recipients)
#
#        return render_to_response('submit_thanks.html', context)
#        
#    context['error'] = error
#    return render_to_response('search_form.html', context)






















