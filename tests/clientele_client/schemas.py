from __future__ import annotations

import inspect
import typing

import pydantic

from clientele.schemas import ListResponse  # noqa


class Input(pydantic.BaseModel):
    limit: int = 20
    offset: int = 0


class OrderingSchema(pydantic.BaseModel):
    order: typing.Literal["random"] | list[str] = []


class PageFilterSchema(pydantic.BaseModel):
    type_: list[str] = pydantic.Field(default=[], alias="type")
    ancestor_of: int | None
    child_of: int | typing.Literal["root"] | None
    descendant_of: int | typing.Literal["root"] | None
    translation_of: int | typing.Literal["root"] | None
    locale: str | None
    site: str | None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class SearchSchema(pydantic.BaseModel):
    search: str | None
    search_operator: str | None


class BasePageMetaSchema(pydantic.BaseModel):
    type_: str | None = pydantic.Field(default=None, alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BasePageSchema(pydantic.BaseModel):
    meta: BasePageMetaSchema
    id: int
    title: str


class PagedBasePageSchema(pydantic.BaseModel):
    items: list[BasePageSchema]
    count: int


class RichTextRemoval(pydantic.BaseModel):
    tag: str
    action: str
    reason: str
    attribute: str | None = None
    detail: str | None = None


class BlogIndexPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["blog.BlogIndexPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BlogIndexPageSchema(pydantic.BaseModel):
    meta: BlogIndexPageMetaSchema
    id: int
    title: str
    introduction: str | None = None
    image: ImageForeignKeySchema | None | None = None


class BlogPageForeignKeySchema(pydantic.BaseModel):
    meta: AbcBlogpagemetaschema2
    id: int | None = None


class BlogPageSchema(pydantic.BaseModel):
    meta: AbcBlogpagemetaschema1
    id: int
    title: str
    introduction: str | None = None
    subtitle: str | None = None
    date_published: str | None = None
    image: ImageForeignKeySchema | None | None = None
    body: list[typing.Any] = []
    tags: list[str] = []
    blog_person_relationship: list[BlogPersonRelationshipSchema] = []


class BlogPersonRelationshipMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["blog.BlogPersonRelationship"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BlogPersonRelationshipSchema(pydantic.BaseModel):
    meta: BlogPersonRelationshipMetaSchema
    id: int | None = None
    page: typing.Any | None = None
    person: typing.Any | None = None


class BreadPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadPageSchema(pydantic.BaseModel):
    meta: BreadPageMetaSchema
    id: int
    title: str
    introduction: str | None = None
    ingredients: list[int]
    image: ImageForeignKeySchema | None | None = None
    body: list[typing.Any] = []
    origin: CountryForeignKeySchema | None | None = None
    bread_type: BreadTypeForeignKeySchema | None | None = None


class BreadTypeForeignKeySchema(pydantic.BaseModel):
    meta: BreadTypeMetaSchema
    id: int | None = None


class BreadTypeMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadType"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadsIndexPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadsIndexPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadsIndexPageSchema(pydantic.BaseModel):
    meta: BreadsIndexPageMetaSchema
    id: int
    title: str
    introduction: str | None = None
    image: ImageForeignKeySchema | None | None = None


class CollectionForeignKeySchema(pydantic.BaseModel):
    meta: CollectionMetaSchema
    id: int | None = None


class CollectionMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["wagtailcore.Collection"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class CountryForeignKeySchema(pydantic.BaseModel):
    meta: CountryMetaSchema
    id: int | None = None


class CountryMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.Country"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class FormFieldMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.FormField"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class FormFieldSchema(pydantic.BaseModel):
    meta: FormFieldMetaSchema
    id: int | None = None
    clean_name: str | None = ""
    label: str
    field_type: str
    help_text: str | None = None
    required: bool = True
    choices: str | None = None
    default_value: str | None = None


class FormPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.FormPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class FormPageSchema(pydantic.BaseModel):
    meta: FormPageMetaSchema
    id: int
    title: str
    from_address: str | None = None
    to_address: str | None = None
    subject: str | None = None
    form_fields: list[FormFieldSchema] = []
    image: ImageForeignKeySchema | None | None = None
    body: list[typing.Any] = []
    thank_you_text: str | None = None


class GalleryPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.GalleryPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class GalleryPageSchema(pydantic.BaseModel):
    meta: GalleryPageMetaSchema
    id: int
    title: str
    introduction: str | None = None
    image: ImageForeignKeySchema | None | None = None
    body: list[typing.Any] = []
    collection: CollectionForeignKeySchema | None | None = None


class HomePageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.HomePage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class HomePageSchema(pydantic.BaseModel):
    meta: HomePageMetaSchema
    id: int
    title: str
    hero_text: str
    hero_cta: str
    lead_title: str | None = None
    featured_section_1_title: str | None = None
    featured_section_2_title: str | None = None
    featured_section_3_title: str | None = None
    image: ImageForeignKeySchema | None | None = None
    hero_cta_link: PageForeignKeySchema | None | None = None
    body: list[typing.Any] = []
    lead_image: ImageForeignKeySchema | None | None = None
    lead_text: str | None = None
    featured_section_1: PageForeignKeySchema | None | None = (
        None
    )
    featured_section_2: PageForeignKeySchema | None | None = (
        None
    )
    featured_section_3: PageForeignKeySchema | None | None = (
        None
    )


class ImageForeignKeySchema(pydantic.BaseModel):
    meta: ImageMetaSchema
    id: int | None = None


class ImageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["wagtailimages.Image"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class LocationOperatingHoursMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["locations.LocationOperatingHours"] = pydantic.Field(
        alias="type"
    )
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class LocationOperatingHoursSchema(pydantic.BaseModel):
    meta: LocationOperatingHoursMetaSchema
    id: int | None = None
    day: str = "MON"
    opening_time: str | None = None
    closing_time: str | None = None
    closed: bool | None = None
    get_day_display: typing.Any | None = None


class LocationPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["locations.LocationPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class LocationPageSchema(pydantic.BaseModel):
    meta: LocationPageMetaSchema
    id: int
    title: str
    introduction: str | None = None
    address: str
    lat_long: str
    image: ImageForeignKeySchema | None | None = None
    body: list[typing.Any] = []
    is_open: typing.Any | None = None
    hours_of_operation: list[LocationOperatingHoursSchema] = []


class LocationsIndexPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["locations.LocationsIndexPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class LocationsIndexPageSchema(pydantic.BaseModel):
    meta: LocationsIndexPageMetaSchema
    id: int
    title: str
    introduction: str | None = None
    image: ImageForeignKeySchema | None | None = None


class PageForeignKeySchema(pydantic.BaseModel):
    meta: AbcPagemetaschema2
    id: int | None = None


class PageSchema(pydantic.BaseModel):
    meta: AbcPagemetaschema1
    id: int | None = None
    title: str


class PeopleIndexPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["people.PeopleIndexPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PeopleIndexPageSchema(pydantic.BaseModel):
    meta: PeopleIndexPageMetaSchema
    id: int
    title: str
    introduction: str | None = None
    image: ImageForeignKeySchema | None | None = None


class PersonForeignKeySchema(pydantic.BaseModel):
    meta: PersonMetaSchema
    id: int | None = None


class PersonMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.Person"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PersonPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["people.PersonPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PersonPageSchema(pydantic.BaseModel):
    meta: PersonPageMetaSchema
    id: int
    title: str
    introduction: str | None = None
    image: ImageForeignKeySchema | None | None = None
    body: list[typing.Any] = []
    location: CountryForeignKeySchema | None | None = None
    social_links: list[typing.Any] = []


class RecipeIndexPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["recipes.RecipeIndexPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class RecipeIndexPageSchema(pydantic.BaseModel):
    meta: RecipeIndexPageMetaSchema
    id: int
    title: str
    introduction: str | None = None


class RecipePageForeignKeySchema(pydantic.BaseModel):
    meta: AbcRecipepagemetaschema2
    id: int | None = None


class RecipePageSchema(pydantic.BaseModel):
    meta: AbcRecipepagemetaschema1
    id: int
    title: str
    date_published: str | None = None
    subtitle: str | None = None
    introduction: str | None = None
    backstory: list[typing.Any] = []
    recipe_headline: str | None = None
    body: list[typing.Any] = []
    recipe_person_relationship: list[RecipePersonRelationshipSchema] = []


class RecipePersonRelationshipMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["recipes.RecipePersonRelationship"] = pydantic.Field(
        alias="type"
    )
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class RecipePersonRelationshipSchema(pydantic.BaseModel):
    meta: RecipePersonRelationshipMetaSchema
    id: int | None = None
    page: typing.Any | None = None
    person: typing.Any | None = None


class SimpleBasePageMetaSchema(pydantic.BaseModel):
    type_: str | None = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None
    detail_url: str | None
    html_url: str | None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class SimpleBasePageSchema(pydantic.BaseModel):
    meta: SimpleBasePageMetaSchema
    id: int
    title: str


class StandardPageMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.StandardPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class StandardPageSchema(pydantic.BaseModel):
    meta: StandardPageMetaSchema
    id: int
    title: str
    introduction: str | None = None
    image: ImageForeignKeySchema | None | None = None
    body: list[typing.Any] = []


class AbcBlogpagemetaschema1(pydantic.BaseModel):
    type_: typing.Literal["blog.BlogPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class AbcBlogpagemetaschema2(pydantic.BaseModel):
    type_: typing.Literal["blog.BlogPage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class AbcPagemetaschema1(pydantic.BaseModel):
    type_: typing.Literal["wagtailcore.Page"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class AbcPagemetaschema2(pydantic.BaseModel):
    type_: typing.Literal["wagtailcore.Page"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class AbcRecipepagemetaschema1(pydantic.BaseModel):
    type_: typing.Literal["recipes.RecipePage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    html_url: str | None = None
    locale: str | None = None
    slug: str
    first_published_at: str | None = None
    show_in_menus: bool | None = None
    seo_title: str | None = None
    search_description: str | None = None
    alias_of: SimpleBasePageSchema | None | None = None
    parent: SimpleBasePageSchema | None | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class AbcRecipepagemetaschema2(pydantic.BaseModel):
    type_: typing.Literal["recipes.RecipePage"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BlogIndexPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["blog.BlogIndexPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BlogIndexPageCreateSchema(pydantic.BaseModel):
    meta: BlogIndexPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class BlogPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["blog.BlogPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BlogPageCreateSchema(pydantic.BaseModel):
    meta: BlogPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False
    introduction: str | None = None
    image_id: int | None = None
    body: list[typing.Any] = []
    subtitle: str | None = None
    tags: list[str] = []
    date_published: str | None = None
    blog_person_relationship: list[BlogPersonRelationshipCreateSchema] = []


class BlogPersonRelationshipCreateSchema(pydantic.BaseModel):
    person_id: int


class BreadPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadPageCreateSchema(pydantic.BaseModel):
    meta: BreadPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class BreadsIndexPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadsIndexPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadsIndexPageCreateSchema(pydantic.BaseModel):
    meta: BreadsIndexPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class FormPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.FormPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class FormPageCreateSchema(pydantic.BaseModel):
    meta: FormPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class GalleryPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.GalleryPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class GalleryPageCreateSchema(pydantic.BaseModel):
    meta: GalleryPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class HomePageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.HomePage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class HomePageCreateSchema(pydantic.BaseModel):
    meta: HomePageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class LocationPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["locations.LocationPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class LocationPageCreateSchema(pydantic.BaseModel):
    meta: LocationPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class LocationsIndexPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["locations.LocationsIndexPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class LocationsIndexPageCreateSchema(pydantic.BaseModel):
    meta: LocationsIndexPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class PeopleIndexPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["people.PeopleIndexPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PeopleIndexPageCreateSchema(pydantic.BaseModel):
    meta: PeopleIndexPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class PersonPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["people.PersonPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PersonPageCreateSchema(pydantic.BaseModel):
    meta: PersonPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class RecipeIndexPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["recipes.RecipeIndexPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class RecipeIndexPageCreateSchema(pydantic.BaseModel):
    meta: RecipeIndexPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class RecipePageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["recipes.RecipePage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class RecipePageCreateSchema(pydantic.BaseModel):
    meta: RecipePageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False
    recipe_headline: str | RichTextInputSchema = ""


class RichTextInputSchema(pydantic.BaseModel):
    format: str = "db_html"
    content: str
    removals: list[RichTextRemoval] = []


class StandardPageCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.StandardPage"] = pydantic.Field(alias="type")
    parent_id: int
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class StandardPageCreateSchema(pydantic.BaseModel):
    meta: StandardPageCreateMetaSchema
    title: str
    slug: str | None = None
    seo_title: str | None = None
    search_description: str | None = None
    show_in_menus: bool | None = False


class BlogIndexPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["blog.BlogIndexPage"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BlogIndexPagePatchSchema(pydantic.BaseModel):
    meta: BlogIndexPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class BlogPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["blog.BlogPage"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BlogPagePatchSchema(pydantic.BaseModel):
    meta: BlogPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False
    introduction: str | None
    image_id: int | None
    body: list[typing.Any] = []
    subtitle: str | None
    tags: list[str] = []
    date_published: str | None
    blog_person_relationship: list[BlogPersonRelationshipPatchSchema] = []


class BlogPersonRelationshipPatchSchema(pydantic.BaseModel):
    id: int | None
    person_id: int | None


class BreadPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadPage"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadPagePatchSchema(pydantic.BaseModel):
    meta: BreadPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class BreadsIndexPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadsIndexPage"] | None = pydantic.Field(
        alias="type"
    )
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadsIndexPagePatchSchema(pydantic.BaseModel):
    meta: BreadsIndexPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class FormPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.FormPage"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class FormPagePatchSchema(pydantic.BaseModel):
    meta: FormPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class GalleryPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.GalleryPage"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class GalleryPagePatchSchema(pydantic.BaseModel):
    meta: GalleryPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class HomePagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.HomePage"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class HomePagePatchSchema(pydantic.BaseModel):
    meta: HomePagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class LocationPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["locations.LocationPage"] | None = pydantic.Field(
        alias="type"
    )
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class LocationPagePatchSchema(pydantic.BaseModel):
    meta: LocationPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class LocationsIndexPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["locations.LocationsIndexPage"] | None = pydantic.Field(
        alias="type"
    )
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class LocationsIndexPagePatchSchema(pydantic.BaseModel):
    meta: LocationsIndexPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class PeopleIndexPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["people.PeopleIndexPage"] | None = pydantic.Field(
        alias="type"
    )
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PeopleIndexPagePatchSchema(pydantic.BaseModel):
    meta: PeopleIndexPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class PersonPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["people.PersonPage"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PersonPagePatchSchema(pydantic.BaseModel):
    meta: PersonPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class RecipeIndexPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["recipes.RecipeIndexPage"] | None = pydantic.Field(
        alias="type"
    )
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class RecipeIndexPagePatchSchema(pydantic.BaseModel):
    meta: RecipeIndexPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class RecipePagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["recipes.RecipePage"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class RecipePagePatchSchema(pydantic.BaseModel):
    meta: RecipePagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False
    recipe_headline: str | RichTextInputSchema = ""


class StandardPagePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.StandardPage"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class StandardPagePatchSchema(pydantic.BaseModel):
    meta: StandardPagePatchMetaSchema | None
    title: str | None
    slug: str | None
    seo_title: str | None
    search_description: str | None
    show_in_menus: bool | None = False


class RevisionFilterSchema(pydantic.BaseModel):
    created_at_from: str | None
    created_at_to: str | None
    user_id: int | str | None
    approved_go_live_at_from: str | None
    approved_go_live_at_to: str | None
    object_str: str | None


class BaseMetaSchema(pydantic.BaseModel):
    type_: str = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PagedRevisionSchema(pydantic.BaseModel):
    items: list[RevisionSchema]
    count: int


class RevisionSchema(pydantic.BaseModel):
    meta: BaseMetaSchema
    id: int
    object_id: str
    created_at: str
    user_id: int | str | str | None = None
    object_str: str
    approved_go_live_at: str | None = None


class ContentTypeSchema(pydantic.BaseModel):
    meta: BaseMetaSchema
    id: int
    name: str
    label: str


class PageRevisionDetailSchema(pydantic.BaseModel):
    meta: BaseMetaSchema
    id: int
    object_id: str
    created_at: str
    user_id: int | str | str | None = None
    object_str: str
    approved_go_live_at: str | None = None
    content_type: ContentTypeSchema
    base_content_type: ContentTypeSchema
    content_object: PageSchema | StandardPageSchema | HomePageSchema | GalleryPageSchema | FormPageSchema | BlogPageSchema | BlogIndexPageSchema | BreadPageSchema | BreadsIndexPageSchema | LocationsIndexPageSchema | LocationPageSchema | RecipePageSchema | RecipeIndexPageSchema | PersonPageSchema | PeopleIndexPageSchema


class PageUnpublishSchema(pydantic.BaseModel):
    recursive: bool = False


class PageCopySchema(pydantic.BaseModel):
    destination_id: int | None
    recursive: bool = False
    keep_live: bool = True
    slug: str | None
    title: str | None


class PageMoveSchema(pydantic.BaseModel):
    destination_id: int
    position: str | None = None


class PageRevertSchema(pydantic.BaseModel):
    revision_id: int


class PageCreateAliasSchema(pydantic.BaseModel):
    destination_id: int | None
    recursive: bool = False
    slug: str | None


class PageCopyForTranslationSchema(pydantic.BaseModel):
    locale: str
    copy_parents: bool = False
    alias: bool = False
    recursive: bool = False


class ContentTypeListSchema(pydantic.BaseModel):
    types: list[ContentTypeSummarySchema]


class ContentTypeSummarySchema(pydantic.BaseModel):
    name: str
    label: str


class SchemaDetailResponse(pydantic.BaseModel):
    read: dict[str, typing.Any] | None
    create: dict[str, typing.Any] | None
    patch: dict[str, typing.Any] | None


class PagedSiteSchema(pydantic.BaseModel):
    items: list[SiteSchema]
    count: int


class SiteSchema(pydantic.BaseModel):
    id: int
    hostname: str
    port: int
    site_name: str
    root_page_id: int
    is_default_site: bool


class SiteInputSchema(pydantic.BaseModel):
    hostname: str
    port: int = 80
    site_name: str = ""
    root_page_id: int
    is_default_site: bool = False


class WhoAmIProfileSchema(pydantic.BaseModel):
    avatar_url: str | None


class WhoAmISchema(pydantic.BaseModel):
    user: WhoAmIUserSchema
    profile: WhoAmIProfileSchema
    groups: list[str]


class WhoAmIUserSchema(pydantic.BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    is_superuser: bool


class TranslationFilterSchema(pydantic.BaseModel):
    locale: str | None
    translation_of: str | None


class BreadIngredientMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadIngredient"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadIngredientSchema(pydantic.BaseModel):
    meta: BreadIngredientMetaSchema
    id: int | None = None
    name: str


class BreadTypeSchema(pydantic.BaseModel):
    meta: BreadTypeMetaSchema
    id: int | None = None
    title: str


class FooterTextMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.FooterText"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class FooterTextSchema(pydantic.BaseModel):
    meta: FooterTextMetaSchema
    id: int | None = None
    body: str | None = None


class PagedAnnotated(pydantic.BaseModel):
    items: list[
        BreadIngredientSchema | BreadTypeSchema | FooterTextSchema | PersonSchema
    ]
    count: int


class PersonSchema(pydantic.BaseModel):
    meta: PersonMetaSchema
    id: int | None = None
    first_name: str
    last_name: str
    job_title: str
    image: ImageForeignKeySchema | None | None = None


class BreadIngredientCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadIngredient"] | None = pydantic.Field(
        alias="type"
    )
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadIngredientCreateSchema(pydantic.BaseModel):
    meta: BreadIngredientCreateMetaSchema | None | None = None
    name: str


class BreadTypeCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadType"] | None = pydantic.Field(alias="type")

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadTypeCreateSchema(pydantic.BaseModel):
    meta: BreadTypeCreateMetaSchema | None | None = None
    title: str


class FooterTextCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.FooterText"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class FooterTextCreateSchema(pydantic.BaseModel):
    meta: FooterTextCreateMetaSchema | None
    body: str | RichTextInputSchema = ""


class PersonCreateMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.Person"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PersonCreateSchema(pydantic.BaseModel):
    meta: PersonCreateMetaSchema | None | None = None
    first_name: str
    last_name: str
    job_title: str
    image_id: int | None = None


class BreadIngredientPatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadIngredient"] | None = pydantic.Field(
        alias="type"
    )
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadIngredientPatchSchema(pydantic.BaseModel):
    meta: BreadIngredientPatchMetaSchema | None
    name: str | None


class BreadTypePatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["breads.BreadType"] | None = pydantic.Field(alias="type")

    model_config = pydantic.ConfigDict(populate_by_name=True)


class BreadTypePatchSchema(pydantic.BaseModel):
    meta: BreadTypePatchMetaSchema | None
    title: str | None


class FooterTextPatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.FooterText"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class FooterTextPatchSchema(pydantic.BaseModel):
    meta: FooterTextPatchMetaSchema | None
    body: str | RichTextInputSchema = ""


class PersonPatchMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["base.Person"] | None = pydantic.Field(alias="type")
    action: typing.Literal["publish"] | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class PersonPatchSchema(pydantic.BaseModel):
    meta: PersonPatchMetaSchema | None
    first_name: str | None
    last_name: str | None
    job_title: str | None
    image_id: int | None


class SnippetRevisionDetailSchema(pydantic.BaseModel):
    meta: BaseMetaSchema
    id: int
    object_id: str
    created_at: str
    user_id: int | str | str | None = None
    object_str: str
    approved_go_live_at: str | None = None
    content_type: ContentTypeSchema
    base_content_type: ContentTypeSchema
    content_object: BreadIngredientSchema | BreadTypeSchema | FooterTextSchema | PersonSchema


class SnippetRevertSchema(pydantic.BaseModel):
    revision_id: int


class SnippetCopyForTranslationSchema(pydantic.BaseModel):
    locale: str


class DocumentDetailMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["wagtaildocs.Document"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    tags: list[str] = []
    download_url: str | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class DocumentSchema(pydantic.BaseModel):
    meta: DocumentDetailMetaSchema
    id: int | None = None
    title: str
    collection: CollectionForeignKeySchema


class PagedDocumentSchema(pydantic.BaseModel):
    items: list[DocumentSchema]
    count: int


class DocumentCreateSchema(pydantic.BaseModel):
    title: str
    collection_id: int | None = None


class DocumentPatchSchema(pydantic.BaseModel):
    title: str | None
    collection_id: int | None


class ImageDetailMetaSchema(pydantic.BaseModel):
    type_: typing.Literal["wagtailimages.Image"] = pydantic.Field(alias="type")
    warnings: list[RichTextRemoval | str] | None = None
    detail_url: str | None = None
    tags: list[str] = []
    download_url: str | None = None

    model_config = pydantic.ConfigDict(populate_by_name=True)


class ImageSchema(pydantic.BaseModel):
    meta: ImageDetailMetaSchema
    id: int | None = None
    title: str
    width: int
    height: int
    description: str | None = None
    collection: typing.Any | None = None
    focal_point_x: int | None = None
    focal_point_y: int | None = None
    focal_point_width: int | None = None
    focal_point_height: int | None = None


class PagedImageSchema(pydantic.BaseModel):
    items: list[ImageSchema]
    count: int


class ImageCreateSchema(pydantic.BaseModel):
    title: str
    description: str | None = ""
    collection_id: int | None = None
    focal_point_x: int | None = None
    focal_point_y: int | None = None
    focal_point_width: int | None = None
    focal_point_height: int | None = None


class ImagePatchSchema(pydantic.BaseModel):
    title: str | None
    description: str | None = ""
    collection_id: int | None
    focal_point_x: int | None
    focal_point_y: int | None
    focal_point_width: int | None
    focal_point_height: int | None


class LocaleSchema(pydantic.BaseModel):
    meta: BaseMetaSchema
    id: int
    language_code: str
    display_name: str
    is_bidi: bool
    is_default: bool


class PagedLocaleSchema(pydantic.BaseModel):
    items: list[LocaleSchema]
    count: int


class LocaleInputSchema(pydantic.BaseModel):
    language_code: str


class PagedRedirectSchema(pydantic.BaseModel):
    items: list[RedirectSchema]
    count: int


class RedirectSchema(pydantic.BaseModel):
    id: int
    old_path: str
    site_id: int | None
    is_permanent: bool
    redirect_page_id: int | None
    redirect_page_route_path: str
    redirect_link: str
    automatically_created: bool
    created_at: str | None


class RedirectInputSchema(pydantic.BaseModel):
    old_path: str
    site: int | None = None
    is_permanent: bool = True
    redirect_page_id: int | None = None
    redirect_page_route_path: str = ""
    redirect_link: str = ""


Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)


class Data(pydantic.BaseModel):
    pass


Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)
Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)
Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)


class Data(pydantic.BaseModel):
    pass


Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)
Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)


class PagesActionsUnpublishApplicationJson(pydantic.BaseModel):
    pass


Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)


class PagesActionsCopyApplicationJson(pydantic.BaseModel):
    pass


Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)
Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)
Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)
Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)


class PagesActionsCreateAliasApplicationJson(pydantic.BaseModel):
    pass


Response = (
    PageSchema
    | StandardPageSchema
    | HomePageSchema
    | GalleryPageSchema
    | FormPageSchema
    | BlogPageSchema
    | BlogIndexPageSchema
    | BreadPageSchema
    | BreadsIndexPageSchema
    | LocationsIndexPageSchema
    | LocationPageSchema
    | RecipePageSchema
    | RecipeIndexPageSchema
    | PersonPageSchema
    | PeopleIndexPageSchema
)
Response = BreadIngredientSchema | BreadTypeSchema | FooterTextSchema | PersonSchema


class Data(pydantic.BaseModel):
    pass


Response = BreadIngredientSchema | BreadTypeSchema | FooterTextSchema | PersonSchema
Response = BreadIngredientSchema | BreadTypeSchema | FooterTextSchema | PersonSchema


class Data(pydantic.BaseModel):
    pass


Response = BreadIngredientSchema | FooterTextSchema | PersonSchema
Response = BreadIngredientSchema | FooterTextSchema | PersonSchema
Response = BreadIngredientSchema | BreadTypeSchema | FooterTextSchema | PersonSchema


class MultiPartBodyParams(pydantic.BaseModel):
    file: str
    title: str
    collection_id: int | None = None


class MultiPartBodyParams(pydantic.BaseModel):
    file: str
    title: str
    description: str | None = ""
    collection_id: int | None = None
    focal_point_x: int | None = None
    focal_point_y: int | None = None
    focal_point_width: int | None = None
    focal_point_height: int | None = None


def get_subclasses_from_same_file() -> list[type[pydantic.BaseModel]]:
    """
    Due to how Python declares classes in a module,
    we need to update_forward_refs for all the schemas generated
    here in the situation where there are nested classes.
    """
    calling_frame = inspect.currentframe()
    if not calling_frame:
        return []
    else:
        calling_frame = calling_frame.f_back
    module = inspect.getmodule(calling_frame)

    subclasses = []
    for _, c in inspect.getmembers(module):
        if (
            inspect.isclass(c)
            and issubclass(c, pydantic.BaseModel)
            and c != pydantic.BaseModel
        ):
            subclasses.append(c)

    return subclasses


subclasses: list[type[pydantic.BaseModel]] = get_subclasses_from_same_file()
for c in subclasses:
    c.model_rebuild()
