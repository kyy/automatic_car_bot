
s_s = '+'    # split symbol in filter
s_b = '?'    # skip button on keyboards

# constants of columns:keyboards: max = 8, default = 4
columns_motor = 3
columns_years = 5
columns_cost = 5
columns_dimension = 8

# root links
av_root_link = 'https://av.by/'
abw_root_link = 'https://abw.by/cars'
onliner_root_link = 'https://ab.onliner.by/'

# parse of data for buttons
# make '' for delete button

motor_dict = {'бензин': 'b', 'бензин (пропан-бутан)': 'bpb', 'бензин (метан)': 'bm', 'бензин (гибрид)': 'bg',
              'дизель': 'd', 'дизель (гибрид)': 'dg', 'электро': 'e'}

motor = [s_b] + \
        ['бензин', 'дизель', 'электро', 'дизель (гибрид)', 'бензин (метан)', 'бензин (гибрид)', 'бензин (пропан-бутан)']

transmission = [s_b] + ['автомат', 'механика']

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
}







