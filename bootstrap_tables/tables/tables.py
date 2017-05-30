# coding: utf-8
from __future__ import unicode_literals

# from django_tables2 import Table
# from django.contrib.auth.models import User,UserManager
import numpy as np
import pandas as pd

class TableMetaClass(type):

    def __new__(cls, name, bases, attrs):
        attrs['_meta'] = opts = TableOptions(name,attrs.get('Meta', None))
        return super(TableMetaClass, cls).__new__(cls, name, bases, attrs)

class TableOptions(object):
    def __init__(self, cls_name, options=None):
        super(TableOptions, self).__init__()
        self.container_id = getattr(options, 'container_id', cls_name+'Container')
        self.table_id = getattr(options, 'table_id', cls_name)
        self.url = getattr(options, 'url', '')
        self.attrs = getattr(options, 'attrs', {})
        self.row_attrs = getattr(options, 'row_attrs', {})
        self.pinned_row_attrs = getattr(options, 'pinned_row_attrs', {})
        self.default = getattr(options, 'default', '—')
        self.empty_text = getattr(options, 'empty_text', 'Empty')
        self.fields = getattr(options, 'fields', None)
        self.exclude = getattr(options, 'exclude', ())
        self.order_by = getattr(options, 'order_by', None)
        self.order_by_field = getattr(options, 'order_by_field', 'sort')
        self.page_field = getattr(options, 'page_field', 'page')
        self.per_page = getattr(options, 'per_page', 25)
        self.per_page_field = getattr(options, 'per_page_field', 'per_page')
        self.prefix = getattr(options, 'prefix', '')
        self.show_header = getattr(options, 'show_header', True)

        self.template = getattr(options, 'template', 'bootstrap_table/table.html')
        self.localize = getattr(options, 'localize', ())
        self.unlocalize = getattr(options, 'unlocalize', ())

        # table attribute
        self.db = getattr(options, 'db', 'default')
        self.app = getattr(options, 'app', '')
        self.model = getattr(options, 'model', '')
        self.table_id = getattr(options, 'table_id', 'table')
        self.pk = getattr(options, 'pk', '')

        # column attribute
        self.sequence = getattr(options, 'sequence', [])
        self.orderable = getattr(options, 'orderable', [])
        self.searchable = getattr(options, 'searchable', {})
        self.editable = getattr(options, 'editable', {})
        self.sortable = getattr(options, 'sortable', [])
        self.formattable = getattr(options, 'formattable', [])


class Table(metaclass=TableMetaClass):

    def __init__(self, data, container_id=None, table_id=None):
        super(Table, self).__init__()
        self.data = data
        self.container_id = self._meta.container_id
        self.table_id = self._meta.table_id
        self.url = self._meta.url
        self.attrs = self._meta.attrs
        self.sequence = self._meta.sequence
        self.orderable = self._meta.orderable
        self.searchable = self._meta.searchable
        self.editable = self._meta.editable
        self.sortable = self._meta.sortable
        self.formattable = self._meta.formattable

        self.db = self._meta.db
        self.app = self._meta.app
        self.model = self._meta.model
        self.table_id = self._meta.table_id
        self.pk = self._meta.pk
        self.empty_text = self._meta.empty_text

        self.data=self.order_columns(self.data,self.sequence)
        self.index=self.get_index(self.data,self.pk)
        self.columns=self.get_columns(self.data)

        self.auto = {
                     'table':'',
                     'thead':'',
                     'tbody':'',
                     'tr':'',
                     'th':'',
                     'td':'',
                     }

        self.init_auto()

    def init_auto(self):
        self.shape = self.data.shape

        #init th
        self.auto['th']=np.dstack((self.columns, self.auto_th_attrs()))

        #init td
        self.auto['td']=np.dstack((self.data.values, self.auto_td_attrs()))

    def order_columns(self,data,sequence):

        if sequence and len(sequence)==len(data.columns):
            data = data.reindex_axis(sequence, axis=1)
        return data

    def get_index(self,data,pk):
        if pk:
            index = data[pk].values
        else:
            index = data.index.tolist()

        return index

    def get_columns(self,data):
        columns = data.columns.tolist()
        return columns

    def auto_th_attrs(self):
        # t0=time.clock()
        attrs=pd.DataFrame(columns=self.columns,index=['attrs','sortable','editable','searchable','formattable']).fillna('')

        # init data-field
        for i in attrs.columns.values:
            attrs.loc['attrs',i]=' data-field="{field_name}"'.format(field_name=i)

        #init sortable

        sortable_columns=list(set(self.sortable) & set(self.columns))
        if sortable_columns:
            attrs.loc['sortable',sortable_columns]=' data-sortable="true"'

        #init editable

        editable_columns=list(set(self.editable) & set(self.columns))
        if editable_columns:
            for i in editable_columns:
                if self.editable[i]['type'] == 'text':
                    attrs.loc['editable',i]=' data-editable="true"' \
                                            ' data-editable-type="text"'\
                                            ' data-editable-title={title}'.format(title=self.editable[i]['title'])

                if self.editable[i]['type'] == 'select':
                    attrs.loc['editable',i]=' data-editable="true"' \
                                            ' data-editable-type="select"' \
                                            ' data-editable-title="{title}"'.format(title=self.editable[i]['title'])\
                                           +' data-editable-source={source}'.format(source=self.editable[i]['source'])

        #init searchable
        searchable_columns=list(set(self.searchable.keys()) & set(self.columns))
        if searchable_columns:
            for i in searchable_columns:
                attrs.loc['searchable',i]=' data-filter-control="{type}"'.format(type= self.searchable[i])

        #init formattable
        formattable_columns=list(set(self.formattable) & set(self.columns))
        if formattable_columns:
            for i in formattable_columns:
                attrs.loc['formattable',i]=' data-formatter=' + str(i) + 'Formatter'

        attrs.loc['attrs',:] +=attrs.loc['sortable',:]\
                              +attrs.loc['editable',:]\
                              +attrs.loc['searchable',:]\
                              +attrs.loc['formattable',:]

        # print(time.clock()-t0)
        return attrs.loc['attrs',:].values

    # create unique id and other attrs for each table data
    def auto_td_attrs(self):
        # t0=time.clock()
        td_attrs = pd.DataFrame(columns=self.columns, index=self.index).fillna('')
        for j in range(td_attrs.shape[1]):
            for i in range(td_attrs.shape[0]):
                td_attrs.iat[i, j] += ' id="' + '|'.join(
                    [self.db,self.app, self.model,self.pk, str(td_attrs.index[i]), str(td_attrs.columns[j])])+'"'
        # print(time.clock()-t0)
        return td_attrs.values

# class testTable(Table):
#
#     col1 = 'a'
#
#     class Meta:
#         model = 'test'
#
#         attrs = {'table': """
#                                 id="table"
#                                 data-unique-id="{{ table.pk }}"
#                                 data-toolbar="#toolbar"
#                                 data-striped="true"
#                                 data-search="true"
#                                 data-show-refresh="true"
#                                 data-show-toggle="true"
#                                 data-show-columns="true"
#                                 data-show-export="true"
#                                 data-show-multi-sort="true"
#                                 data-minimum-count-columns="2"
#                                 data-show-pagination-switch="true"
#                                 data-pagination="true"
#                                 data-page-list="[10, 25, 50, 100, ALL]"
#                                 data-show-footer="false"
#                                 data-filter-control="true"
#                                 data-filter-show-clear="true"
#                                 data-click-to-select="true"
#                               """,
#                  'thead': '',
#                  'tbody': '',
#                  'tr': '',
#                  'th': '',
#                  'td': ''}

# if __name__ == "__main__":
#     data = pd.DataFrame({'a':1,'b':2},columns=['a','b'],index=[0])
#     testTable(data)
