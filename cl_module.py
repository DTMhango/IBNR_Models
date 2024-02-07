import pandas as pd
import chainladder as cl
import warnings

warnings.filterwarnings(action='ignore', category=UserWarning)

def create_triangles(data, start_date, end_date):
    dff = data[(data['LOSS DATE'] >= start_date) & (data['PAID DATE'] <= end_date)]
    triangles = cl.Triangle(
        data=dff,
        origin='LOSS DATE',
        development='PAID DATE',
        columns=['GROSS AMOUNT', 'NET AMOUNT'],
        index=['MAIN CLASS', 'ADDITIONAL SEGMENTATION'],
        cumulative=False
    )
    return triangles


def create_os_triangles(data, start_date, end_date):
    dff = data[(data['LOSS DATE'] >= start_date) & (data['OUTSTANDING DATE'] <= end_date)]
    triangles = cl.Triangle(
        data=dff,
        origin='LOSS DATE',
        development='OUTSTANDING DATE',
        columns=['GROSS AMOUNT', 'NET AMOUNT'],
        index=['MAIN CLASS', 'ADDITIONAL SEGMENTATION'],
        cumulative=False
    )
    return triangles


def tri_size(triangle):
    size = triangle.shape[2]
    return size


def pure_ibnr(ibnr_triangle, os_triangle):
    total = []
    dates = []
    zeroized = []
    if tri_size(ibnr_triangle) == tri_size(os_triangle):
        for i in range(tri_size(ibnr_triangle)):
            if ibnr_triangle.origin_grain == 'Y':
                dates.append(ibnr_triangle.origin[i].strftime('%F'))
            elif ibnr_triangle.origin_grain == 'Q':
                dates.append(
                    ibnr_triangle.origin[i].strftime('%F-Q%q'))
            elif ibnr_triangle.origin_grain == 'M':
                dates.append(ibnr_triangle.origin[i].strftime('%F-%m'))
            else:
                dates.append(
                    ibnr_triangle.origin[i].strftime('%F-Q%q'))
            
            if os_triangle.iat[0, 0, i, 0] != os_triangle.iat[0, 0, i, 0]:
                emerging = ibnr_triangle.iat[0, 0,
                                         i, 0]
            else:
                emerging = ibnr_triangle.iat[0, 0,
                                            i, 0] - os_triangle.iat[0, 0, i, 0]
                
            total.append(emerging)
            if emerging >= 0:
                zeroized.append(emerging)
            elif emerging < 0:
                zeroized.append(0)
            elif emerging != emerging:
                zeroized.append(0)

        pure_ibnr_dict = {'Pure IBNR': total}
        pure_ibnr_df = (pd.DataFrame(pure_ibnr_dict, index=dates))

        total_row_pure = pd.DataFrame(
            {'Pure IBNR': [pure_ibnr_df['Pure IBNR'].sum()]}, index=['TOTAL'])
        pure_ibnr_df = pd.concat([pure_ibnr_df, total_row_pure])

        zeroized_dict = {'Zeroized Pure IBNR': zeroized}
        zeroized_df = (pd.DataFrame(zeroized_dict, index=dates))

        total_row_zeroized = pd.DataFrame(
            {'Zeroized Pure IBNR': [zeroized_df['Zeroized Pure IBNR'].sum()]}, index=['TOTAL'])
        zeroized_df = pd.concat([zeroized_df, total_row_zeroized])

        return pure_ibnr_df, zeroized_df
