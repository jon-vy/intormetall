import threading
import time
import requests
from lxml import html

# <editor-fold desc="Получить ссылки для парса">
def get_url():
    r = requests.get('https://intormetall.ru/')
    html_body = html.fromstring(r.text)
    links = html_body.xpath("//li[@class='no']/ul/li/a[@href]")
    link_list = []
    for i in range(len(links)):
        link = f"https://intormetall.ru{links[i].attrib['href']}"
        link_list.append(link)
        #print(link, len(link_list))

    return link_list
# </editor-fold>
# <editor-fold desc="Парсинг">
def pars(url):
    print(url)
    r = requests.get(url)
    html_body = html.fromstring(r.text)
    availability = html_body.xpath("//td[@class='it3']") # проверка на наличие
    try:
        price_unit = html_body.xpath("//nobr/text()[contains(., '(руб/')]")[0]
    except: pass
    for i in range(len(availability)):
        try:
            int(availability[i].text)
            title = html_body.xpath("//span[@itemprop='name']")[i].text
            price = html_body.xpath("//span[@itemprop='price']")[i].text
            add_product(title, price, price_unit)
            print(f"{title} | {price} | {price_unit}")
        except: pass
# </editor-fold>
# <editor-fold desc="Записать в базу">
def add_product(name, price, price_unit):
    supplier_id = get_suppliers_id()
    response = requests.post(
        'https://prod.pkf-m.ru/parser-api/v1/parser/intormet/products/',  # suppliers/
        headers={
            'accept': '*/*',
            'apikey': 'qDas8ppyF4Hrw2ZRbrBXWSkuNbO0gL',
            'Content-Type': 'application/json'
                 },
        json=[{
            "name": name,
            "price": price,
            "price_unit": price_unit,
            "supplier_id": supplier_id
        }]
    )
    if response.status_code == 200:
        print("Записано в базу")
# </editor-fold>
# <editor-fold desc="Очистить базу">
def clear_database():
    response = requests.delete(
        'https://prod.pkf-m.ru/parser-api/v1/parser/intormet/products/',
        headers={
            'accept': '*/*',
            'apikey': 'qDas8ppyF4Hrw2ZRbrBXWSkuNbO0gL'
        }
    )
    print(response.text)
    print(response)
# </editor-fold>
# <editor-fold desc="Получить id поставщика">
def get_suppliers_id():
    response = requests.get(
        'https://prod.pkf-m.ru/parser-api/v1/parser/intormet/suppliers/',
        headers={
            'accept': 'application/json',
            'apikey': 'qDas8ppyF4Hrw2ZRbrBXWSkuNbO0gL'
        }
    )
    try:
        supplier_id = response.json()[0]['id']
    except:
        response = requests.post(
            'https://prod.pkf-m.ru/parser-api/v1/parser/intormet/supplier/',
            headers={
                'accept': '*/*',
                'apikey': 'qDas8ppyF4Hrw2ZRbrBXWSkuNbO0gL',
                'Content-Type': 'application/json'
            },
            json={
                'name': 'Интрометалл',
                'city': 'г.Долгопрудный',
                'contacts': 'Иола Муратиди 8(495)9213567 доб.102 iola@intormetall.ru',
                'address': 'г.Долгопрудный Лихачевский проезд 14',
                'notes': '',
                'raiting': 0
            }
        )
        supplier_id = response.json()['supplier']['id']
        # print(suppliers_id)
    return supplier_id
# </editor-fold>


if __name__ == '__main__':
    start = time.monotonic()
    clear_database()
    link_list = get_url()

    # <editor-fold desc="В один поток">
    # for i in range(len(link_list)):
    #     pars(link_list[i])
    # </editor-fold>

    # <editor-fold desc="многопоток">
    thr_list = []
    for i in range(len(link_list)):
        thr = threading.Thread(target=pars, args=(link_list[i],))  # создал поток
        thr_list.append(thr)
        thr.start()
    for i in thr_list:
        i.join()
    # </editor-fold>

    end = time.monotonic()
    result_time = end - start
    print(f"Время работы: {result_time}")
    input('Нажмите Enter для выхода\n')
