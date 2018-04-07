import pandas as pd


class ChildPlantPartsReport:

    @classmethod
    def get_data(cls):
        data = pd.read_csv('Child Plants Master.csv', encoding='iso-8859-1')
        data['Total Value'] = data['Qty On-Hand'] * data['Cost']
        data['Location'] = data['Location'].apply(lambda x: str(x))
        # print(data)
        return data

    @classmethod
    def run_report(cls):

        data = cls.get_data()
        # result = data.groupby(['Parts Id', 'Plant']).apply(cls.agg_fun)
        # result = data.groupby(['Parts Id', 'Plant']).agg({'Parts Id': 'count',
        #                                                   'Qty On-Hand': 'sum',
        #                                                   'Location': lambda x: ','.join(x)
        #                                                   })\
        #                                             .rename(columns={'Parts Id': '1Match',
        #                                                              'Qty On-Hand': '2Qty',
        #                                                              'Location': '3Loc'
        #                                                              })
        #
        # result = result.unstack('Plant', fill_value='')
        # result = pd.DataFrame(result).reset_index()
        # result.columns = result.columns.swaplevel(0, 1)
        # result.sortlevel(0, axis=1, inplace=True)

        result_ = data.groupby(['Parts Id']).agg({'Parts Id': 'count',
                                                  'Description': lambda x: x,
                                                  'Manufacturer': lambda x: x,
                                                  'Qty On-Hand': 'sum',
                                                  'Cost': 'mean',
                                                  'Total Value': 'sum'
                                                          })\
                                                  .rename(columns={'Parts Id': 'Total Somax Match',
                                                                   'Manufacturer': 'Brand',
                                                                   'Qty On-Hand': 'Total Somax Qty',
                                                                   'Cost': 'Avg Somax Cost',
                                                                   'Total Value': 'Total Somax Value'
                                                                   })
        result_.reset_index()


        # data_ = data[['Parts Id', 'Description', 'Manufacturer']].set_index('Parts Id')
        # result = result.join(result_, on='Parts Id')

        # result.to_csv('result.csv')
        result_.to_csv('result_.csv', encoding='iso-8859-1')

        # print(result)

    @staticmethod
    def agg_fun(x):
        # print(x)
        return pd.Series(dict(
                              Location=','.join(x)))


if __name__ == "__main__":

    ChildPlantPartsReport.run_report()