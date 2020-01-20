from typing import Union

from fastapi import APIRouter, Depends
from starlette.requests import Request

from optimade.models import (
    ErrorResponse,
    ReferenceResource,
    ReferenceResponseMany,
    ReferenceResponseOne,
)
from optimade.server.config import CONFIG
from optimade.server.deps import EntryListingQueryParams, SingleEntryQueryParams
from optimade.server.entry_collections import MongoCollection, client
from optimade.server.mappers import ReferenceMapper

from .utils import get_entries, get_single_entry


router = APIRouter()

references_coll = MongoCollection(
    collection=client[CONFIG.mongo_database][CONFIG.references_collection],
    resource_cls=ReferenceResource,
    resource_mapper=ReferenceMapper,
)


@router.get(
    "/references",
    response_model=Union[ReferenceResponseMany, ErrorResponse],
    response_model_exclude_unset=True,
    tags=["References"],
)
def get_references(request: Request, params: EntryListingQueryParams = Depends()):
    return get_entries(
        collection=references_coll,
        response=ReferenceResponseMany,
        request=request,
        params=params,
    )


@router.get(
    "/references/{entry_id:path}",
    response_model=Union[ReferenceResponseOne, ErrorResponse],
    response_model_exclude_unset=True,
    tags=["References"],
)
def get_single_reference(
    request: Request, entry_id: str, params: SingleEntryQueryParams = Depends()
):
    return get_single_entry(
        collection=references_coll,
        entry_id=entry_id,
        response=ReferenceResponseOne,
        request=request,
        params=params,
    )
