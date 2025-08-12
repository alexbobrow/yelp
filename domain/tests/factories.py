import factory
from factory import Factory

from domain.models import Building, Activity, Phone, Company, CompanySummary
from tests.fields import ListSubFactory


class BuildingFactory(Factory):
    class Meta:
        model = Building

    id = factory.Sequence(lambda n: n)
    address = factory.Faker("address", locale="ru_RU")
    longitude = factory.Faker("longitude")
    latitude = factory.Faker("latitude")


class PhoneFactory(Factory):
    class Meta:
        model = Phone

    id = factory.Sequence(lambda n: n)
    number = factory.Faker("phone_number", locale="ru_RU")


class ActivityFactory(Factory):
    class Meta:
        model = Activity

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("sentence", nb_words=3, locale="ru_RU")


class CompanyFactory(Factory):
    class Meta:
        model = Company

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("large_company", locale="ru_RU")
    legal_form = factory.Faker("company_prefix", locale="ru_RU")
    building = factory.SubFactory(BuildingFactory)
    phones = ListSubFactory(PhoneFactory, size=2)
    activities = ListSubFactory(ActivityFactory, size=2)


class CompanySummaryFactory(Factory):
    class Meta:
        model = CompanySummary

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("large_company", locale="ru_RU")
    legal_form = factory.Faker("company_prefix", locale="ru_RU")
