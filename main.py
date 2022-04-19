import requests
import bs4
import lxml
import pprint
import csv

for i in range(1, 36):
    url = f'https://www.wildberries.ru/catalog/sport/vidy-sporta/turizm-kemping/snaryazhenie/turisticheskaya-mebel?page={i}'
    response = requests.get(url)
    content = response.text

    soup = bs4.BeautifulSoup(content, 'lxml')
    products = soup.find_all('div', class_='product-card')
    category = soup.find('h1', class_='catalog-title').text.strip()
    data = {
        category: []
    }

    for product in products:
        common_name = product.find('div', class_='product-card__brand-name')
        brand = common_name.find('strong', class_='brand-name').text.replace('/', '').strip()
        good = common_name.find('span', class_='goods-name').text.strip()
        common_price = product.find('div', class_='product-card__price')
        price = common_price.find('span', class_='lower-price')  # Может вернуть None
        # Обход цены без скидки
        if price:
            strip_price = price.text.strip()
            strip_price_encode = strip_price.encode('ascii', 'ignore')
            strip_price_decode = int(strip_price_encode.decode())
        else:
            lower_price = common_price.find('ins', class_='lower-price').text.strip()
            lower_price_encode = lower_price.encode('ascii', 'ignore')  # удаление unicode символов
            lower_price_decode = int(lower_price_encode.decode())  # кодиорвание обратно

            old_price = common_price.find('span', class_='price-old-block').text.strip()
            old_price_encode = old_price.encode('ascii', 'ignore')
            old_price_decode = int(old_price_encode.decode())

        data[category].append({
            'Бренд': brand,
            'Товар': good,
            'Цена': {'Цена по скидке': '-', 'Цена без скидки': strip_price_decode} if price
            else {'Цена по скидке': lower_price_decode, 'Цена без скидки': old_price_decode}
        })

for g in data[category]:
    pprint.pprint(g)

with open('parsed_data.csv', 'w', encoding='utf-8', ) as csv_file:
    fields = ['Бренд', 'Товар', 'Цена', 'Цена по скидке']
    writer = csv.writer(csv_file)
    writer.writerow(fields)
    for row in data[category]:
        row_data = row.get('Бренд'), row.get('Товар'), \
                   row.get('Цена').get('Цена без скидки'), row.get('Цена').get('Цена по скидке')
        print(row_data)
        writer.writerow(row_data)
