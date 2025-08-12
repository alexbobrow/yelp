import factory
from factory import Factory
from faker import Faker
from geoalchemy2 import WKTElement

from config.const import COORDS_SYSTEM_2D
from infrastructure.models.models import CompanyOrm, BuildingOrm, PhoneOrm, ActivityOrm


fake = Faker()


class BuildingOrmFactory(Factory):
    class Meta:
        model = BuildingOrm

    address = factory.Faker("address", locale="ru_RU")
    coordinates = factory.LazyFunction(
        lambda: WKTElement(f"POINT({fake.longitude()} {fake.latitude()})", srid=COORDS_SYSTEM_2D)
    )


class CompanyOrmFactory(Factory):
    class Meta:
        model = CompanyOrm

    name = factory.Faker("large_company", locale="ru_RU")
    legal_form = factory.Faker("company_prefix", locale="ru_RU")


class PhoneOrmFactory(Factory):
    class Meta:
        model = PhoneOrm

    number = factory.Faker("phone_number", locale="ru_RU")


class ActivityOrmFactory(Factory):
    class Meta:
        model = ActivityOrm

    name = factory.Faker("sentence", nb_words=3, locale="ru_RU")
