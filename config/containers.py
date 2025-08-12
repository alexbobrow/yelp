from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration

from config.database import DbManager
from config.settings import Settings
from infrastructure.repositories.company import CompanyRepository
from usecases.company import GetCompanyByIdUseCase, CompaniesListUseCase


class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(
        modules=[
            "api.v1.company",
        ],
    )

    settings = providers.Singleton(Settings)
    db = providers.Factory(DbManager, settings=settings)
    company_repo = providers.Factory(CompanyRepository, session=db.provided.session, settings=settings)
    get_company_by_id_uc = providers.Factory(GetCompanyByIdUseCase, company_repo=company_repo)
    companies_list_uc = providers.Factory(CompaniesListUseCase, company_repo=company_repo)
