from mongoengine import Document, UUIDField, EmailField, StringField, \
    BooleanField, ListField, DictField, DateTimeField, FloatField, ImageField, \
    IntField, EmbeddedDocument, ObjectIdField, ReferenceField, \
    EmbeddedDocumentField, DynamicField

from uuid import uuid4
from datetime import datetime, date
import calendar

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import URLSafeTimedSerializer as URLSerializer
from itsdangerous import BadSignature, SignatureExpired

from flask import current_app

AdminPermissions = ('super_user', 'mod_admin', 'admin_user')


class AdminUser(Document):
    meta = {'strict': 'False'}
    id = UUIDField(primary_key=True, default=uuid4)
    name = StringField()
    email = EmailField()
    password_hash = StringField()
    permissions = StringField(choices=AdminPermissions)
    login_log = DictField()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.cofirmed = True
        self.save()
        return True


ProductCategory = ('Refrigerator', 'Washing Machine',
                   'Microwave Oven', 'Television', 'Furniture')
ProductConditions = ('Like New', 'Gently Used',
                     'Rusted', 'Unboxed', 'Well Used')

OrderStates = ('Processing', 'Order Placed', 'Confirmed',
               'Shipped', 'Delivered', 'Canceled', 'Returned')
PaymentModes = ('COD', 'online', 'card')


class Carousel(Document):
    file_name = StringField(unique=True)
    image = ImageField()


class CartItem(EmbeddedDocument):
    code = StringField()
    quantity = IntField()


class Address(EmbeddedDocument):
    id = UUIDField(primary_key=True, default=uuid4)
    address = StringField()
    zip_code = StringField()
    city = StringField()


class User(Document):
    meta = {'strict': 'False'}
    id = UUIDField(primary_key=True, default=uuid4)
    name = StringField()
    email = EmailField(unique=True)
    password_hash = StringField()
    confirmed = BooleanField(default=False)
    contact_number = StringField()
    conf_otp = IntField(default=000000)
    contact_verified = BooleanField(default=False)
    shipping_address = ListField(EmbeddedDocumentField(Address))
    billing_address = EmbeddedDocumentField(Address)
    referrals_list = ListField()
    signup_timestamp = DateTimeField(default=datetime.utcnow())
    login_log = DictField()
    cart = ListField(DictField())
    coupons = ListField(StringField())

    def generate_auth_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'email': self.email}).decode('utf-8')

    def generate_confirm_token(self):
        s = URLSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': str(self.id)})

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def confirm(self, token):
        s = URLSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=3600)
        except:
            return False
        if data['id'] == str(self.id):
            self.confirmed = True
            self.save()
            return True
        return False

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        except TypeError:
            return None
        user = User.objects.get(email=data['email'])
        return user


class ProductImage(EmbeddedDocument):
    image_name = StringField()
    product_image = ImageField()


class Product(Document):

    meta = {'indexes': [
        {'fields': ['$name', "$description", "$code", "$specifications", "$category", "$condition"],
         'default_language': 'english'
         }
    ]}

    id = UUIDField(primary_key=True, default=uuid4)
    name = StringField()
    description = StringField()
    specifications = DictField()
    code = StringField(unique=True)
    price = FloatField()
    mrp = FloatField()
    minimum_discounted_price = FloatField()
    images = ListField(EmbeddedDocumentField(ProductImage))
    warranty = IntField()  # Warranty in months
    units = IntField()
    category = StringField(choices=ProductCategory)
    instock = BooleanField(default=False)
    condition = StringField(choices=ProductConditions)
    archive = BooleanField(default=False)
    discount_percentage = IntField(default=0)


class OrderProducts(EmbeddedDocument):
    id = UUIDField(primary_key=True, default=uuid4)
    name = StringField()
    description = StringField()
    specifications = DynamicField()
    images = ListField(EmbeddedDocumentField(ProductImage))
    code = StringField()
    quantity = IntField(default=1)
    warranty = IntField()  # Warranty in months
    category = StringField(choices=ProductCategory)
    warranty_expiry = DateTimeField()
    warranty_claims = IntField(default=0)
    condition = StringField()
    price = FloatField()
    discount_percentage = IntField(default=0)

    def warranty_date_setter(self):
        today = date.today()
        month = today.month - 1 + self.warranty
        year = int(today.year + self.warranty / 12)
        month = month % 12 + 1
        day = min(today.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)


class Order(Document):
    meta = {'indexes': [
        {'fields': ['$order_id', "$payment_id"],
         'default_language': 'english'
         }
    ]}
    id = UUIDField(primary_key=True, default=uuid4)
    order_id = StringField(unique=True)
    user = ReferenceField(User)
    products = ListField(EmbeddedDocumentField(OrderProducts))
    tax = FloatField()
    discount = FloatField(default=0.0)
    coupon_applied = StringField(default=None)
    total = FloatField()
    order_placed = DateTimeField(default=datetime.utcnow())
    delivery_address = EmbeddedDocumentField(Address)
    billing_address = EmbeddedDocumentField(Address)
    order_canceled = DateTimeField()
    status = StringField(chocies=OrderStates, default='Processing')
    status_log = DictField()
    payment_mode = StringField(chocies=PaymentModes)
    payment_request_id = StringField()
    payment_id = StringField()


class Coupon(Document):
    id = UUIDField(primary_key=True, default=uuid4)
    coupon_code = StringField(unique=True)
    discount = IntField(default=0)  # 0 to 100
    discount_amount = IntField(default=0)
    minimum_order_price = FloatField()
