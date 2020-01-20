"""
Main interface for codestar-notifications service client paginators.

Usage::

    import boto3
    from mypy_boto3.codestar_notifications import (
        ListEventTypesPaginator,
        ListNotificationRulesPaginator,
        ListTargetsPaginator,
    )

    client: CodeStarNotificationsClient = boto3.client("codestar-notifications")

    list_event_types_paginator: ListEventTypesPaginator = client.get_paginator("list_event_types")
    list_notification_rules_paginator: ListNotificationRulesPaginator = client.get_paginator("list_notification_rules")
    list_targets_paginator: ListTargetsPaginator = client.get_paginator("list_targets")
"""
# pylint: disable=arguments-differ,redefined-outer-name,redefined-builtin
from typing import Generator, List, TYPE_CHECKING
from botocore.paginate import Paginator as Boto3Paginator
from mypy_boto3_codestar_notifications.type_defs import (
    ListEventTypesFilterTypeDef,
    ListEventTypesResultTypeDef,
    ListNotificationRulesFilterTypeDef,
    ListNotificationRulesResultTypeDef,
    ListTargetsFilterTypeDef,
    ListTargetsResultTypeDef,
    PaginatorConfigTypeDef,
)


__all__ = ("ListEventTypesPaginator", "ListNotificationRulesPaginator", "ListTargetsPaginator")


class ListEventTypesPaginator(Boto3Paginator):
    """
    [Paginator.ListEventTypes documentation](https://boto3.amazonaws.com/v1/documentation/api/1.11.6/reference/services/codestar-notifications.html#CodeStarNotifications.Paginator.ListEventTypes)
    """

    def paginate(
        self,
        Filters: List[ListEventTypesFilterTypeDef] = None,
        PaginationConfig: PaginatorConfigTypeDef = None,
    ) -> Generator[ListEventTypesResultTypeDef, None, None]:
        """
        [ListEventTypes.paginate documentation](https://boto3.amazonaws.com/v1/documentation/api/1.11.6/reference/services/codestar-notifications.html#CodeStarNotifications.Paginator.ListEventTypes.paginate)
        """


class ListNotificationRulesPaginator(Boto3Paginator):
    """
    [Paginator.ListNotificationRules documentation](https://boto3.amazonaws.com/v1/documentation/api/1.11.6/reference/services/codestar-notifications.html#CodeStarNotifications.Paginator.ListNotificationRules)
    """

    def paginate(
        self,
        Filters: List[ListNotificationRulesFilterTypeDef] = None,
        PaginationConfig: PaginatorConfigTypeDef = None,
    ) -> Generator[ListNotificationRulesResultTypeDef, None, None]:
        """
        [ListNotificationRules.paginate documentation](https://boto3.amazonaws.com/v1/documentation/api/1.11.6/reference/services/codestar-notifications.html#CodeStarNotifications.Paginator.ListNotificationRules.paginate)
        """


class ListTargetsPaginator(Boto3Paginator):
    """
    [Paginator.ListTargets documentation](https://boto3.amazonaws.com/v1/documentation/api/1.11.6/reference/services/codestar-notifications.html#CodeStarNotifications.Paginator.ListTargets)
    """

    def paginate(
        self,
        Filters: List[ListTargetsFilterTypeDef] = None,
        PaginationConfig: PaginatorConfigTypeDef = None,
    ) -> Generator[ListTargetsResultTypeDef, None, None]:
        """
        [ListTargets.paginate documentation](https://boto3.amazonaws.com/v1/documentation/api/1.11.6/reference/services/codestar-notifications.html#CodeStarNotifications.Paginator.ListTargets.paginate)
        """
