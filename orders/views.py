from django.shortcuts import render
from django.http import HttpResponse
import requests
from datetime import datetime, timedelta

def dashboard_view(request):

    context = {
        "connected": False,
        "has_data": False,
        "data": {
            'date': "",
            'units_in_use': 0,
            'units_available': 0,
            'persons_quarantined': 0,
            'non_close_contacts': 0,
            'count_consistent': False
        },
        "centres": []
    }
    td = datetime.today()
    qs_d = ""
    occupancy_data = []
    quarantine_data = []

    for d in range(8):
        td = td - timedelta(days=d)
        print(td)
        qs_d = f"{td.strftime('%d')}%2F{td.strftime('%m')}%2F{td.strftime('%Y')}"
        print(qs_d)
        try:
            occupancy_data = requests.get(f"https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Foccupancy_of_quarantine_centres_eng.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%2C%22sorts%22%3A%5B%5B8%2C%22desc%22%5D%5D%2C%22filters%22%3A%5B%5B1%2C%22eq%22%2C%5B%22{qs_d}%22%5D%5D%5D%7D").json()
            quarantine_data = requests.get(f"https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Fno_of_confines_by_types_in_quarantine_centres_eng.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%2C%22filters%22%3A%5B%5B1%2C%22eq%22%2C%5B%22{qs_d}%22%5D%5D%5D%7D").json()
            print(f"INFO: Successfully Connected to APIs at date {td}")
            context['connected'] = True
            # print(len(occupancy_data), len(quarantine_data))
        except Exception as ex:
            print(f"Failed to reach endpoints at {td}. Details: {ex}")
            context['connected'] = False
            context['has_data'] = False
            break
        
        if len(occupancy_data) > 0 and len(quarantine_data) == 1:
            context['has_data'] = True
            context['data']['date'] = td.strftime('%d/%m/%Y')

            units_in_use = 0
            units_available = 0
            persons_quarantined = 0
            non_close_contacts = 0
            centres = []
            for idx, centre in enumerate(occupancy_data):
                units_in_use += centre['Current unit in use']
                units_available += centre['Ready to be used (unit)']
                persons_quarantined += centre['Current person in use']
                if idx < 3:
                    centres.append({
                        'name': centre['Quarantine centres'],
                        'units': centre['Ready to be used (unit)']
                    })
            non_close_contacts = quarantine_data[0]['Current number of non-close contacts'] 
            count_consistent = quarantine_data[0]['Current number of close contacts of confirmed cases'] == persons_quarantined

            context['data']['units_in_use'] = units_in_use
            context['data']['units_available'] = units_available
            context['data']['persons_quarantined'] = persons_quarantined
            context['data']['non_close_contacts'] = non_close_contacts
            context['data']['count_consistent'] = count_consistent
            context['centres'] = centres
            print(context)
            break
        else:
            print(f"INFO: no data at date {td}")
            print(occupancy_data, quarantine_data)
            continue

    else:
        context['connected'] = True
        context['has_data'] = False
        print(f"Connected but no data within the past 7 days.")
        


    
    return render(request, 'dashboard3.html', context=context)