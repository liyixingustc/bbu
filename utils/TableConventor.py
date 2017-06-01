import pandas as pd


class TableConvertor:

    @classmethod
    def df_week_view(cls, data, name='name', date='date', duration='duration'):

        data[date] = (data[date].apply(lambda x: '{date}<br/>{week}'.format(date=str(x),week=x.strftime('%a'))))
        data[duration] = data[duration].apply(lambda x: x.total_seconds()/3600)
        data = pd.pivot_table(data,values=duration,index=name,columns=date).reset_index()
        data.rename_axis(None,inplace=True)

        return data