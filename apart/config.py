from task.const import *

app_config = {
    'name': 'apart',
    'app_title': 'communal',
    'icon': 'building',
    'role': ROLE_APART,
    'views': {
        'apart': {
            'icon': 'building', 
            'title': 'apartments',
            'item_name': 'apartment',
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'star', 
            'title': 'services',
        },
        'meter': {
            'role': ROLE_METER,
            'icon': 'star', 
            'title': 'meters data',
            'item_name': 'meters data',
            'add_button': True,
        },
        'price': {
            'role': ROLE_PRICE,
            'icon': 'star', 
            'title': 'prices',
        },
        'bill': {
            'role': ROLE_BILL,
            'icon': 'star', 
            'title': 'bills',
        },
    }
}