from bootstrap_tables.tables.tables import Table


class WorkSchedulerPanel2Table1(Table):

    class Meta:
        table_id = 'WorkSchedulerPanel2Table1TableId'
        container_id = 'WorkSchedulerPanel2Table1ContainerId'

        attrs = {'table': """
                            id="{table_id}"
                            data-striped="true"
                            data-minimum-count-columns="2"
                            data-show-footer="false"
                            data-pagination="true"
                            data-filter-control="true"
                            data-filter-show-clear="true"
                          """.format(table_id=table_id),
                 'thead': '',
                 'tbody': '',
                 'tr': '',
                 'th': '',
                 'td': '',
                 }

        url = {'edit': 'Panel2/Table1/Edit/'}
