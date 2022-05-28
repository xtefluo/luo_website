import json
import pytz
import uuid

from django.utils.timezone import datetime
from django.utils.timezone import zoneinfo
import pandas as pd
from django_pandas.io import read_frame
from django.core.paginator import Paginator
from django.core.cache import cache
from django.shortcuts import render
from django.http import JsonResponse
from django_q.tasks import async_task
from .models import Order, Course, SearchRecord
from . import data_analysis

PAYMENT_PENDING, PAYMENT_SUCCESS, PAYMENT_CANCELLED, PAYMENT_OVERDUE, PAYMENT_REFUND  = "PE", "SU", "CA", "OV", "RE"
STATUS_TYPE_CHOICES = dict([
    (PAYMENT_PENDING, '未支付'),
     (PAYMENT_SUCCESS, '支付成功'),
      (PAYMENT_CANCELLED, '取消'),
       (PAYMENT_OVERDUE, '过期'),
        (PAYMENT_REFUND, '退款'),
])

op_to_lookup = {
    'equal': 'exact',
    'not_equal': 'exact',
    'like': 'contains',
    'not_like': 'contains',
    'starts_with': 'startswith',
    'ends_with': 'endswith',
    'less': 'lt',
    'less_or_equal': 'lte',
    'greater': 'gt',
    'greater_or_equal': 'gte',
    'between': 'range',
    'not_between': 'range',
    'select_equals': 'exact',
    'select_not_equals': 'exact',
    'select_any_in': 'in',
    'select_not_any_in': 'in',
}

data_analysis_function_map = {
    'platform_pie': data_analysis.get_platform_pie,
    'product_line_income_bar': data_analysis.get_product_line_income_bar,
    'daily_income_line': data_analysis.get_daily_income_line,
    'total_income_text': data_analysis.get_total_income_text,
    'provinces_sales_map': data_analysis.get_provinces_sales_map,
}

def order_data_vis_api(request):
    data_type = request.GET.get('type', '')
    data = {
        'status': 0,
        'msg': 'ok',
        'data':{}
    }

    sid = request.GET.get('sid', '')
    if len(sid) == 0:
        return JsonResponse(data)

    cache_data = cache.get(sid)
    orders_df = pd.read_json(cache_data, orient='table')
    # orders = SearchRecord.objects.get(id = sid).objs.all()
    # orders_df = read_frame(orders, coerce_float = True)
    data_analysis_function = data_analysis_function_map[data_type]
    data['data'] = data_analysis_function(orders_df)

    # if data_type == 'platform_pie':
    #     platform_counts = orders_df['platform'].value_counts()
    #     platform_data = [{'name':name, 'value':value} for name,value in platform_counts.items()]
    #     data['data'] = {
    #         'platform_data' : platform_data
    #     }
    #
    # # if data_type == 'platform_pie':
    # #     data['data'] = {
    # #         'platform_data':[
    # #             {'name':'iOS', 'value':100},
    # #             {'name':'Android', 'value':100}
    # #         ]
    # #     }
    # elif data_type == 'product_line_income_bar':
    #     data['data'] = {
    #         'x_data': ['A产品线', 'B产品线', 'C产品线'],
    #         'y_data': [300, 200, 100]
    #     }
    # elif data_type == 'daily_income_line':
    #     data['data'] = {
    #         'x_data': ['2022-05-01', '2022-05-02', '2022-05-03'],
    #         'y_data': [300, 100, 500]
    #     }
    return JsonResponse(data)

def index(request):
    order_fields = [{'name':field.name, 'label':field.verbose_name} for field in Order._meta.fields]
    return render(request, 'dashboard/index.html', {'order_fields':order_fields})

def analyse_order_conditions(conditions): # 从后端返回数据
    final_query = None
    for child in conditions['children']: # 重点
        if 'children' in child:
            child_query = analyse_order_conditions(child)
        else:
            model, field = child['left']['field'].split('.')
            lookup = op_to_lookup[child['op']]
            right = child['right']
            if field.endswith('time'):
                if isinstance(right, list):
                    start_dt, end_dt = right
                    start_dt = datetime.strptime(start_dt, '%Y-%m-%dT%H:%M:%S%z')
                    end_dt = datetime.strptime(end_dt, '%Y-%m-%dT%H:%M:%S%z')
                    right = (start_dt, end_dt)
                else:
                    right = datetime.fromtimestamp(right, '%Y-%m-%dT%H:%M:%S%z')

            if model == 'order':
                params = {f'{field}__{lookup}':right} # 重点
            else:
                params = {f'{model}__{field}__{lookup}':right} # 重点

            if 'not_' in child['op']:
                child_query = Order.objects.exclude(**params) # 重点
            else:
                child_query = Order.objects.filter(**params) # 重点

        if final_query is None:
            final_query = child_query
        elif conditions['conjunction'] == 'and':
            final_query = final_query & child_query
        else:
            final_query = final_query | child_query

    return final_query


def order_filter_api(request):
    data = json.loads(request.body.decode())
    page = data.get('page',1)
    per_page = data.get('perPage', 10)
    conditions = data.get('conditions', {})

    orders = analyse_order_conditions(conditions) if len(conditions) > 0 else Order.objects.all()
    orders = orders.order_by('id')
    # orders = Order.objects.all().order_by('id')

    paginator = Paginator(orders, per_page)
    page_obj = paginator.get_page(page)
    items = list(page_obj.object_list.values())
    for item in items:
        item['course'] = Course.objects.get(id = item['course_id']).title
        item['create_time'] = item['create_time'].astimezone(zoneinfo.ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        if item['pay_time'] is not None:
            item['pay_time'] = item['pay_time'].astimezone(zoneinfo.ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        item['status'] = STATUS_TYPE_CHOICES[item['status']]
    # print(list(page_obj.object_list.values()))
    # rows = [
    #     {
    #         'id': '0',
    #         'oid':'1024',
    #         'product_line':'AAA',
    #         'course':'A课程',
    #         'create_time':'20220512',
    #         'user_id':'123456789',
    #         'user_mobile':'15701002288',
    #         'user_address':'中国',
    #         'abtest':'1',
    #         'pay_time':'20220512-19:00',
    #         'pay_channel':'微信',
    #         'status':'支持成功',
    #         'transaction_serial_number':'123343545757863453',
    #         'price':'25567',
    #         'fee_price':'1',
    #         'refund_price':'',
    #         'out_vendor':'',
    #         'platfrom':'ios',
    #     }
    # ]

    data = {
        'status': 0,
        'msg': 'ok',
        'data':{
            'total': orders.count(),
            'items': items
        }
    }

    if len(conditions) > 0:
        # search_record = SearchRecord.objects.create(conditions = json.dumps(conditions)) # 新的类创建方式
        # print(search_record)
        # search_record.objs.add(*orders)
        sid = str(uuid.uuid4())
        data['data']['sid'] = sid

        # orders = SearchRecord.objects.get(id=search_record.id).objs.all()
        orders_df = read_frame(orders, coerce_float=True) # 转DataFrame
        orders_json = orders_df.to_json(orient='table') # 订单转成json格式
        # parsed = json.loads(orders_json) # 将已编码的 JSON 字符串解码为 Python 对象
        # json.dumps(parsed, indent=4) # json.dumps 用于将 Python 对象编码成 JSON 字符串
        cache.set(sid, orders_json, 600)

    return JsonResponse(data)

def order_send_email_api(request):
    sid = request.GET.get('sid')
    body_data = json.loads(request.body.decode())
    email = body_data.get('email')

    email_data = {
        'sid': sid,
        'email':email,
        'subject':'您的订单数据表格已生成'
    }

    async_task('dashboard.tasks.send_email', email_data)

    data = {
        'status': 0,
        'msg': '邮件发送请求已开始处理',
        'data': {

        }
    }

    return JsonResponse(data)

def spider_zhihu_api(request):
    result = cache.get('spider-zhihu', [])
    data = {
        'status': 0,
        'msg': 'ok',
        'data': {
            'total': len(result),
            'items': result
        }
    }

    return JsonResponse(data)