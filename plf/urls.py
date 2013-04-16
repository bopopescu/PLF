from django.conf.urls import patterns, include, url
from info import views
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    #(r'^search/$', views.search),
    (r'^submit/$', views.submit),
    #(r'^submit/thanks/$', views.submitthanks),
    (r'^$', views.home),
    (r'^data/$', views.dataReturn),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
#    (r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.STATIC_ROOT}),
    #(r'^/)
    # Examples:
    # url(r'^$', 'plf.views.home', name='home'),
    # url(r'^plf/', include('plf.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
