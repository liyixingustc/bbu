from bootstrap_tables.tables.tables import Table


class WorkWorkersPanel1Table1(Table):

    class Meta:
        table_id = 'WorkWorkersPanel1Table1'

        attrs = {'table': """
                                id="{table_id}"
                                data-toolbar="#toolbar"
                                data-striped="true"
                                data-search="true"
                                data-show-refresh="true"
                                data-show-toggle="true"
                                data-show-columns="true"
                                data-show-export="true"
                                data-show-multi-sort="true"
                                data-detail-view="true"
                                data-minimum-count-columns="2"
                                data-show-pagination-switch="true"
                                data-pagination="true"
                                data-page-list="[10, 25, 50, 100, ALL]"
                                data-show-footer="false"
                                data-filter-control="true"
                                data-filter-show-clear="true"
                                data-click-to-select="true"
                              """.format(table_id=table_id),
                 'thead': '',
                 'tbody': '',
                 'tr': '',
                 'th': '',
                 'td': '',
                 }

        url = {'detail':'Panel1/Table2/Create/'}


class WorkWorkersPanel1Table2(Table):

    class Meta:
        table_id = 'WorkWorkersPanel1Table2'

        attrs = {'table': """
                                id="{table_id}"
                                data-striped="true"
                                data-minimum-count-columns="2"
                                data-show-footer="false"
                                data-filter-control="true"
                                data-click-to-select="true"
                              """.format(table_id=table_id),
                 'thead': '',
                 'tbody': '',
                 'tr': '',
                 'th': '',
                 'td': '',
                 }