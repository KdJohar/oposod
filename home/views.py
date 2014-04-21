# Django imports
from calendar import monthrange
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from users.models import DailyPhoto, Friends, FeedView
from utils.privacy_decorators import visibility_of_calendar
import json
import operator
from oposod.settings import SITE

# Python imports

@csrf_exempt
def index(request):
    
    dp_dict = {}
    score = {}
    if request.user.is_authenticated():
        try:
            fr_obj = get_object_or_404(Friends, user = request.user)
        except:
            fr_obj = None
        if fr_obj:
            for friend_i in fr_obj.list_of:
                dp_obj = DailyPhoto.objects.filter(is_public = True,
                    user = get_object_or_404(User, id = friend_i))
                if dp_obj:
                    
                    
                    for i in dp_obj:
                        dp_dict[i.id] = i
                        # break
                    score = {}
                    for dp in dp_obj:
                        try:
                            score[dp.id] = dp.likes_set.get(user = request.user).rating
                        except:
                            score[dp.id] = 0
    # print dict((k, v) for k, v in dp_dict.iteritems())
    
    

    try:
        feed_view_obj = FeedView.objects.get(user=request.user)
    except: 
        feed_view_obj = None

    if feed_view_obj and feed_view_obj.view == 'ICON':
        sorted_dp_dict = sorted(dp_dict.iteritems(), key = operator.itemgetter(0), reverse = True)
        return render(request, 'home/index_icon.html', {
        
            'score': score,
            'sorted_dp_dict': sorted_dp_dict,
        })
    else:
        sorted_dp_dict = sorted(dp_dict.iteritems(), key = operator.itemgetter(0), reverse = True)[0:10]
        return render(request, 'home/index.html', {
            
            'score': score,
            'sorted_dp_dict': sorted_dp_dict,
        })


def show_more_index(request, dp_id):
    
    html = ''
    dp_id = int(dp_id)
    dp_dict = {}
    score = {}
    if request.user.is_authenticated():
        try:
            fr_obj = get_object_or_404(Friends, user = request.user)
        except:
            fr_obj = None
        if fr_obj:
            for friend_i in fr_obj.list_of:
                dp_obj = DailyPhoto.objects.filter(id__lt = dp_id, id__gte = int(dp_id - 10), is_public = True,
                    user = get_object_or_404(User, id = friend_i))
                if dp_obj:
                    
                    
                    for i in dp_obj:
                        dp_dict[i.id] = i
                        # break
                    score = {}
                    for dp in dp_obj:
                        try:
                            score[dp.id] = dp.likes_set.get(user = request.user).rating
                        except:
                            score[dp.id] = 0
    # print dict((k, v) for k, v in dp_dict.iteritems())
    
    sorted_dp_dict = sorted(dp_dict.iteritems(), key = operator.itemgetter(0), reverse = True)[0:10]
    return render(request, 'home/show_more_index.html', {
        'sorted_dp_dict': sorted_dp_dict,
        'SITE': SITE,

    })
    # if sorted_dp_dict:
    #     for dp_id, dp_obj in sorted_dp_dict:
    #         print dp_obj

    #         html = html + '''
    #             <div class="main-container">
    #                 <div class="story-container">
    #                     <div id="dyn_photo_%s" class="photo">
    #                         <a title="%s"  href="%s/daily-photo/lightbox/%s"><img src="/media/%s_200x160"> </a>
    #                     </div>

    #                     <div class="story">
    #                         <p style="margin-bottom: -10px;color:#343536;font-size:14px">
    #                             %s
    #                         </p>
    #                         <hr>
    #                         <p style="font-size: 11px;margin-top:-10px;">
    #                             %s...
    #                         </p>
    #                     </div>
    #                     <script>
    #                         $("#dyn_photo_%s").colorbox({fixed:true,width:'%s', height:'%s', href: '%s/%s/daily-photo/lightbox/%s'});
    #                     </script>
    #                 </div>

    #                 <div class="user">''' % (dp_obj.key, 
    #                     dp_obj.heading, dp_obj.user.username, dp_obj.key, 
    #                     dp_obj.photo, dp_obj.heading[0:70], 
    #                     dp_obj.story[0:200],dp_obj.key, "85%", "100%",
    #                     SITE, dp_obj.user.username, dp_obj.key)

    #         for i in dp_obj.user.profilephoto_set.all():
    #             if i.is_set:
    #                 #return HttpResponse(i.profile_photo)
    #                 html = html +  '''<a href="/%s">
    #                 <div class="circular"><img style="margin-top: 30px;" src="/media/%s.220x196_q85%s%s_crop_detail.jpg" />
    #                 </div></a> '''% (dp_obj.user.username, i.profile_photo, '_box-' if i.cropping else '', i.cropping)
                   
                   
    #         html = html + '''<p>
    #                     %s %s
    #                     <br>
    #                    %s 
    #                 </p>
    #             </div>
    #         </div>
    #         '''% (dp_obj.user.first_name, dp_obj.user.last_name, dp_obj.uploaded_on)
    #         #if dp_id == len(your_dict)-1:

    #     html = html + '''<div id="hidden_last_shown_dp_id">
    #                         <input type="hidden" name="dp_id" value="%s" />
    #                      </div>
    #     ''' % (sorted_dp_dict[-1][1].id)


    # else:
    #     html = '<center>No more feed<center>'
    # return HttpResponse(html)


def named_month(month_number):
    """
    Return the name of the month, given the number.
    """
    date_tup = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
       10: "October",
       11: "November",
       12: "December",
    }
    return date_tup[month_number]

def this_month(request):
    """
    Show calendar of events this month.
    """
    today = datetime.now()
    return calendar(request, today.year, today.month)




@visibility_of_calendar
def calendar(request, username, year = None, month = None, series_id = None):
    """
    Show calendar of events for a given month of a given year.
    ``series_id``
    The event series to show. None shows all event series.

    """
    month_name_list = [datetime.strftime(date(2001, 01 + i, 01), "%B") for i in range(12)]
    year_list = [i for i in xrange(datetime.now().year, 1900, -1)]
    print "Post data: ", request.POST
    if request.POST:
        try:
            month = month_name_list.index(str(request.POST['month'])) + 1
            year = int(request.POST['year'])
        except:
            month = None
            year = None

    if year and month:
        year = int(year)
        month = int(month)
        if year == date.today().year and month > date.today().month:
            print "in if"
            my_month = date.today().month
            my_year = date.today().year
        elif year > date.today().year:
            print "in elif"
            my_month = date.today().month
            my_year = date.today().year
        else:
            print "in else"
            my_year = int(year)
            my_month = int(month)
    else:
        my_month = date.today().month
        my_year = date.today().year
    my_calendar_from_month = datetime(my_year, my_month, 1)
    my_calendar_to_month = datetime(my_year, my_month, monthrange(my_year, my_month)[1])
    user_obj = get_object_or_404(User, username = username)
    my_events = DailyPhoto.objects.filter(user = user_obj, is_public = True, uploaded_on__gte = my_calendar_from_month).filter(uploaded_on__lte = my_calendar_to_month)

    '''
    print my_events
    if series_id:
        my_events = my_events.filter(series=series_id)
    '''

    # Calculate values for the calendar controls. 1-indexed (Jan = 1)
    my_previous_year = my_year
    my_previous_month = my_month - 1
    if my_previous_month == 0:
        my_previous_year = my_year - 1
        my_previous_month = 12
    my_next_year = my_year
    my_next_month = my_month + 1
    if my_next_month == 13:
        my_next_year = my_year + 1
        my_next_month = 1
    my_year_after_this = my_year + 1
    my_year_before_this = my_year - 1
    return render_to_response(
        "cal_template.html",
        {   'photo_list': my_events,
            'username': username,
            'user_obj': user_obj,
            'month': my_month,
            'month_name': named_month(my_month),
            'year': my_year,
            'previous_month': my_previous_month,
            'previous_month_name': named_month(my_previous_month),
            'previous_year': my_previous_year,
            'next_month': my_next_month,
            'next_month_name': named_month(my_next_month),
            'next_year': my_next_year,
            'year_before_this': my_year_before_this,
            'year_after_this': my_year_after_this,
            'month_name_list': month_name_list,
            'year_list': year_list,
        },
        context_instance = RequestContext(request)
    )

@login_required
def set_view(request, view_type):
    if request.user.is_authenticated():
        user_obj = request.user
    else:
        user_obj = None

    if user_obj and request.is_ajax():
        feed_view_obj, created  = FeedView.objects.get_or_create(user=user_obj)
        feed_view_obj.view = view_type
        feed_view_obj.save()

    return HttpResponse('')