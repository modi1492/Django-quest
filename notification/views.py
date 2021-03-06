#coding=utf-8
import time
from datetime import datetime,timedelta,tzinfo
import json

from django.shortcuts import render,render_to_response,RequestContext
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.template.loader import render_to_string

from redishelper.timeline_util import get_message_list,get_unread_message_list
from redishelper.timeline import read_message

PAGE_COUNT=20
TIME_STRF="%Y/%m/%d %H:%M:%S"

def get_notification_list(request):
    message_type=request.GET.get("type","unread")
    itmes={}
    if message_type=="unread":
        items=get_unread_message_list(request.user.id,skip=0,count=19)
    else:
        items=get_message_list(request.user.id,skip=0,count=19)
    items["notification_type"]=message_type
    return render_to_response("message.html",items,context_instance=RequestContext(request))

def get_notifications(request):
    message_type=request.GET.get("type","unread")
    endtime=request.GET.get("endtime")
    skip=int(request.GET.get("skip",0))
    try:
        t=time.strptime(endtime,TIME_STRF)
        endtime=datetime(* t[:6],tzinfo=CMT8())
        itmes={}
        if message_type=="unread":
            items=get_unread_message_list(request.user.id,endtime,skip,PAGE_COUNT-1)
        else:
            items=get_message_list(request.user.id,endtime,skip,PAGE_COUNT-1)
        html_str=render_to_string("message_list.html",items)
        endtime=None
        if items["endtime"]:
            endtime=items["endtime"].strftime(TIME_STRF)
        return HttpResponse(json.dumps({"html":html_str,"count":items["count"],"endtime":endtime}))
    except Exception,e:
        return HttpResponse(json.dumps({"html":"","count":None,"endtime":None}))
    


def set_message_read(request):
    message_type=request.GET.get("m",None)
    content_id=request.GET.get("c",None)
    fuser_id=request.GET.get("f",None)
    address=request.GET.get("a",None)
    if message_type and content_id and fuser_id and address:
        read_message(int(content_id),int(message_type),request.user.id,int(fuser_id))
        return HttpResponseRedirect(address)
    return Http404

class CMT8(tzinfo):
    delta=timedelta(hours=0)
    def dst(self,dt):
        return self.delta
    def tzname(self,dt):
        return u"GMT+8"
    def utcoffset(self,dt):
        return self.delta

