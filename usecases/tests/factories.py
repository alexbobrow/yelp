import factory
from factory import Factory

from usecases.company import CompaniesListUseCaseRequest


class CompaniesListUseCaseRequestFactory(Factory):
    class Meta:
        model = CompaniesListUseCaseRequest

    building_id = factory.Faker("pyint")
    activity_id = factory.Faker("pyint")
    activity_children = factory.Faker("pybool")
    name = factory.Faker("pystr")
    lat = factory.Faker("pyfloat")
    lng = factory.Faker("pyfloat")
    radius = factory.Faker("pyint")
    latx = factory.Faker("pyfloat")
    lngx = factory.Faker("pyfloat")
    laty = factory.Faker("pyfloat")
    lngy = factory.Faker("pyfloat")
    offset = factory.Faker("pyint")
