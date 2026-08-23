from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from wagtail import hooks
from wagtail.admin.site_summary import SummaryItem


class WgtlApiCliSummaryItem(SummaryItem):
    order = 50
    template_name = "wgtl_api_cli/admin/wgtl_api_cli_summary.html"


@hooks.register("construct_homepage_summary_items")
def register_wgtl_api_cli_summary_item(request, summary_items):
    summary_items.append(WgtlApiCliSummaryItem(request))


@hooks.register("register_admin_urls")
def register_admin_urls():
    urls = [
        path(
            "jsi18n/",
            JavaScriptCatalog.as_view(packages=["wgtl_api_cli"]),
            name="javascript_catalog",
        ),
        # Add other package-scoped URLs here so they are access-restricted to the admin.
    ]

    return [
        path(
            "wgtl_api_cli/",
            include(
                (urls, "wgtl_api_cli"),
                namespace="wgtl_api_cli",
            ),
        )
    ]
