import json, os, requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from ...models import Product, ProductItem, Category, AttributeOption, Image, AttributeType

class Command(BaseCommand):
    help = 'Импортирует продукты из JSON'
    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        product_path = os.path.join(base_dir, 'dataset', 'product.json')
        iphones_path = os.path.join(base_dir, 'dataset', 'iphone_items')
        base_image_url = 'https://cdn0.ipoint.kz/AfrOrF3gWeDA6VOlDG4TzxMv39O7MXnF4CXpKUwGqRM/resize:fit:230/bg:fff/plain/s3://'
        ending = '@webp'

        urls = self.create_urls(base_dir)
        print('Overall', urls)
        with open(product_path, encoding='utf-8') as f:
            data1 = json.load(f)
        # self.create_products(data1)
        for iphone in os.listdir(iphones_path):
            with open(os.path.join(iphones_path, iphone), encoding='utf-8') as f:
                # data2 is url to particular product item. Since all product items
                # within one product share the same specification
                # we can use the only one as a sample
                data2 = json.load(f)
                self.create_product_items(data2, urls[data2['product']['category'][0]['slug']], base_image_url, ending)

        self.stdout.write(self.style.SUCCESS('Продукты импортированы'))
    def create_urls(self, basedir)->dict:
        urls = {}

        path = os.path.join(basedir, 'dataset', 'iphone_items')

        for item in os.listdir(path):
            with open(os.path.join(path,item), 'r') as f:
                json_file = json.loads(f.read())
                slug = json_file['product']['category'][0]['slug']
                urls[slug]=('https://ispace.kz/api/aktau/apr/catalog/products/category/iphone/'+slug+'?iscorp=0')
        return urls

    def create_products(self,data):
        category_id = Category.objects.get(id=1)
        for child in data['categories']['children']:
            slug = child.get('slug', '')
            name = child.get('name', '')
            # url = child.get('url', '')
            discount = child.get('discount', 0)

            product = Product(category_id=category_id,
                            slug=slug,
                            name=name,
                            # url = url,
                            discount=discount)

            product.save()

    def create_product_items(self,item, url, base_image_url, ending):
        # dataset/iphone_items are data for one particular model (models differs by color and memory)
        # from each group (iphone-16, iphone-16-pro, etc.). Since all iPhone models within one
        # group share the same characteristics, I used these data for retrieving characteristics.
        # the only thing that is differs from one model to another is memory.
        # price depends on memory only.
        # in order to obtain particular price for each possible memory that group could possibly have,
        # I use group data set, where it has 'data' about each model that belongs to this group
        # along with its memory and price
        iPhone = Category.objects.get(name='iPhone')
        product = item['product']

        slug = item['category']['slug']
        product_id = Product.objects.get(slug=slug)

        weight = product['weight']
        discount = 0
        availability = 1
        specification = product['attributes']
        display = specification['Дисплей']['Размер дисплея']
        del specification["Память"]

        data = requests.get(url)
        iphones:list = data.json()['products']['data']
        print('Product Item: ',url)
        for iphone in iphones:
            name = iphone['name']
            memory = iphone['configuration']
            price = float(iphone['prices']['price'])

            # update
            item_slug = iphone['slug']
            sku = iphone['sku']

            try:
                color = iphone['name'].split(', ')[2]
            except:
                continue

            product_item = ProductItem(product_id=product_id,
                                slug=item_slug,
                                sku=sku,
                                name=name,
                                color=color,
                                weight=weight,
                                price=price,
                                discount=discount,
                                availability=availability,
                                specification=specification)

            product_item.save()

            # Working with Attributes
            storage_type = AttributeType.objects.get(type='storage')
            display_type = AttributeType.objects.get(type='display')

            replacements = {
                    'GB': 'ГБ',
                    'TB': 'ТБ'}
            for latin, cyrillic in replacements.items():
                memory = memory.replace(latin, cyrillic)
            memory_option, _= AttributeOption.objects.get_or_create(type_id=storage_type,
                                                                category_id=iPhone,
                                                                option_name=memory)
            display_option, _ = AttributeOption.objects.get_or_create(type_id=display_type,
                                                                category_id=iPhone,
                                                                option_name=display)
            product_item.attribute.add(memory_option, display_option)

            # Working with Images
            image = iphone['image']
            image_url = base_image_url + image + ending
            try:
                print(color)
                image = Image.objects.get(image=f'{slug}/{color}.jpg')
                product_item.image.add(image)
            except:
                self.download_and_attach_image(product_item, image_url, color + '.jpg')

    def download_and_attach_image(self, product_item, image_url, filename):
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image()
            image.save()
            product_item.image.add(image)
            image.image.save(filename, ContentFile(response.content), save=True)
        else:
            print(f"Не удалось скачать изображение: {image_url}")

#filter by Camera, Memory, Display
# delete only Memory block