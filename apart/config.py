from task.const import *

app_config = {
    'name': APP_APART,
    'app_title': 'communal',
    'icon': 'building',
    'role': ROLE_APART,
    'views': {
        'apart': {
            'icon': 'building', 
            'title': 'apartments',
            'item_name': 'apartment',
            'relate': [ROLE_DOC],
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'star', 
            'title': 'services',
        },
        'price': {
            'role': ROLE_PRICE,
            'icon': 'star', 
            'title': 'prices',
            'add_button': True,
        },
        'meter': {
            'role': ROLE_METER,
            'icon': 'star', 
            'title': 'meters data',
            'item_name': 'meters data',
            'add_button': True,
            'relate': [ROLE_TODO],
        },
        'bill': {
            'role': ROLE_BILL,
            'icon': 'star', 
            'title': 'bills',
            'add_button': True,
            'relate': [ROLE_TODO],
       },
    }
}