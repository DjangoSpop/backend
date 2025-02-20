# Generated by Django 5.1.2 on 2024-10-16 11:19

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_productsize_remove_product_barcode_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-created_at'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AlterModelOptions(
            name='productimage',
            options={'ordering': ['created_at'], 'verbose_name': 'Product Image', 'verbose_name_plural': 'Product Images'},
        ),
        migrations.RemoveField(
            model_name='product',
            name='discounted_price',
        ),
        migrations.AddField(
            model_name='product',
            name='barcode',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True, unique=True, verbose_name='Barcode'),
        ),
        migrations.AddField(
            model_name='product',
            name='colors',
            field=models.JSONField(blank=True, default=list, verbose_name='Colors'),
        ),
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Quantity'),
        ),
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Rating'),
        ),
        migrations.AddField(
            model_name='product',
            name='review_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Review Count'),
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.CharField(blank=True, db_index=True, max_length=50, null=True, verbose_name='Subcategory'),
        ),
        migrations.AddField(
            model_name='productimage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created At'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.CharField(db_index=True, max_length=50, verbose_name='Brand'),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(db_index=True, default=django.utils.timezone.now, max_length=50, verbose_name='Category'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='product',
            name='in_stock',
            field=models.BooleanField(default=True, verbose_name='In Stock'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(db_index=True, max_length=100, verbose_name='Product Name'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='product',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to=settings.AUTH_USER_MODEL, verbose_name='Seller'),
        ),
        migrations.RemoveField(
            model_name='product',
            name='sizes',
        ),
        migrations.AlterField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(upload_to='product_images/', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='is_primary',
            field=models.BooleanField(default=False, verbose_name='Is Primary'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='api.product', verbose_name='Product'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['name'], name='api_product_name_73c704_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category'], name='api_product_categor_07b5d3_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['brand'], name='api_product_brand_b832b2_idx'),
        ),
        migrations.AddField(
            model_name='product',
            name='sizes',
            field=models.JSONField(blank=True, default=list, verbose_name='Sizes'),
        ),
    ]
