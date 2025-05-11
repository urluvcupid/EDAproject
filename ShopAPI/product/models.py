from django.db import models


# Create your models here.

class Category(models.Model):
    id = models.AutoField(primary_key=True) #for internal connections
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'Categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(unique=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=50)
    discount = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.name}"

class AttributeType(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    type = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.type}"

class AttributeOption(models.Model):
    type_id = models.ForeignKey(AttributeType, on_delete=models.CASCADE, related_name='options')
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='options', blank=True, null=True)
    option_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('option_name', 'type_id', 'category_id')

    def __str__(self):
        return f"{self.category_id.name}: {self.option_name}"

def upload_to(instance, filename):
    slug = instance.product_items.first().\
            product_id.slug
    return f'{slug}/{filename}'

class Image(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)

class ProductItem(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(unique=True, max_length=100)
    sku=models.CharField(max_length=100)

    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')

    name = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    weight = models.CharField(max_length=7,blank=True, null=True)
    price = models.FloatField(max_length=15)
    discount = models.PositiveSmallIntegerField(default=0)
    availability = models.PositiveSmallIntegerField(default=1)

    attribute = models.ManyToManyField(AttributeOption, related_name='product_items')
    image = models.ManyToManyField(Image, related_name='product_items')
    specification = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.name},{self.attribute.all()}"

# fullfilment
# triggers for slugs
# linkter black for python
# Class Meta for models