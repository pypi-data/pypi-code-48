# This file exists within 'nark':
#
#   https://github.com/hotoffthehamster/nark
#
# Copyright © 2018-2020 Landon Bouma
# Copyright © 2015-2016 Eric Goller
# All  rights  reserved.
#
# 'nark' is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License  as  published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any   later    version.
#
# 'nark' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY  or  FITNESS FOR A PARTICULAR
# PURPOSE.  See  the  GNU General Public License  for  more details.
#
# You can find the GNU General Public License reprinted in the file titled 'LICENSE',
# or visit <http://www.gnu.org/licenses/>.

import datetime

import pytest

from nark.backends.sqlalchemy.objects import (
    AlchemyActivity,
    AlchemyCategory,
    AlchemyFact,
    AlchemyTag
)
from nark.backends.sqlalchemy.storage import SQLAlchemyStore
from nark.config import decorate_config


# The reason we see a great deal of count == 0 statements is to make sure that
# db rollback works as expected. Once we are confident in our sqlalchemy/pytest
# setup those are not really needed.
class TestStore(object):
    """Tests to make sure our store/test setup behaves as expected."""
    def test_build_is_not_persistent(self, alchemy_store, alchemy_category_factory):
        """
        Make sure that calling ``factory.build()`` does not create a
        persistent db entry.
        """
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        alchemy_category_factory.build()
        assert alchemy_store.session.query(AlchemyCategory).count() == 0

    def test_factory_call_persistent(self, alchemy_store, alchemy_category_factory):
        """Make sure that ``factory()`` does creates a persistent db entry."""
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        alchemy_category_factory()
        assert alchemy_store.session.query(AlchemyCategory).count() == 1

    def test_create_is_persistent(self, alchemy_store, alchemy_category_factory):
        """Make sure that  ``create()`` does creates a persistent db entry."""
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        alchemy_category_factory()
        assert alchemy_store.session.query(AlchemyCategory).count() == 1

    def test_build_pk(self, alchemy_store, alchemy_category_factory):
        """Make sure that factory instances have no pk assigned."""
        instance = alchemy_category_factory.build()
        assert instance.pk

    def test_create_pk(self, alchemy_store, alchemy_category_factory):
        """Make sure that factory.create instances have pk assigned."""
        instance = alchemy_category_factory.create()
        assert instance.pk

    def test_instance_fixture(self, alchemy_store, alchemy_category):
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        assert alchemy_category.pk
        assert alchemy_category.name

    def test_get_db_url(self, alchemy_config_parametrized, alchemy_store):
        """Make sure that db_url composition works as expected."""
        config, expectation = alchemy_config_parametrized
        alchemy_store.config = decorate_config(config)
        assert alchemy_store.db_url == expectation

    def test_get_db_url_missing_keys(
        self, alchemy_config_missing_store_config_parametrized, alchemy_store,
    ):
        """
        Make sure that db_url composition throws error if key/values are
        missing in config.
        """
        with pytest.raises(ValueError):
            alchemy_store.config = decorate_config(
                alchemy_config_missing_store_config_parametrized
            )
            # If decorate_config() does not raise on engine missing error,
            # db_url will raise on missing path, host, etc.
            alchemy_store.db_url

    def test_init_with_unicode_path(self, alchemy_config, db_path_parametrized):
        """Test that Instantiating a store with a unicode path works."""
        alchemy_config['db.path'] = db_path_parametrized
        assert SQLAlchemyStore(alchemy_config)


class TestCategoryManager():
    def test_add_new(self, alchemy_store, alchemy_category_factory):
        """
        Our manager methods return the persistant instance as hamster objects.
        As we want to make sure that we compare our expectations against the
        raw saved object, we look it up explicitly again.
        """
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        category = alchemy_category_factory.build().as_hamster(alchemy_store)
        category.pk = None
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        result = alchemy_store.categories._add(category)
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        db_instance = alchemy_store.session.query(AlchemyCategory).get(result.pk)
        assert category.equal_fields(db_instance)
        assert category != db_instance

    def test_add_existing_name(self, alchemy_store, alchemy_category_factory):
        """
        Make sure that adding a category with a name that is already present
        gives an error.
        """
        existing_category = alchemy_category_factory()
        category = alchemy_category_factory.build().as_hamster(alchemy_store)
        category.name = existing_category.name
        category.pk = None
        with pytest.raises(ValueError):
            alchemy_store.categories._add(category)

    def test_add_with_pk(self, alchemy_store, alchemy_category_factory):
        """
        Make sure that adding a alchemy_category that already got an PK
        raises an exception.
        """
        category = alchemy_category_factory().as_hamster(alchemy_store)
        category.name += 'foobar'
        assert category.pk
        with pytest.raises(ValueError):
            alchemy_store.categories._add(category)

    def test_update(
        self, alchemy_store, alchemy_category_factory, new_category_values,
    ):
        """Test that updateing a alchemy_category works as expected."""
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        # (lb): NOTE_TO_SELF: The alchemy_category_factory fixture was created
        # when conftest.py called `register(lib_factories.CategoryFactory)`,
        # which, AFAICT, is the same as calling the factory directly:
        #   alchemy_category_factory = factories.AlchemyCategoryFactory
        category = alchemy_category_factory().as_hamster(alchemy_store)
        new_values = new_category_values(category)
        for key, value in new_values.items():
            assert getattr(category, key) != value
        for key, value in new_values.items():
            setattr(category, key, value)
        alchemy_store.categories._update(category)
        db_instance = alchemy_store.session.query(AlchemyCategory).get(category.pk)
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        assert category.equal_fields(db_instance)

    def test_update_without_pk(self, alchemy_store, alchemy_category_factory):
        """Make sure that passing a category without a PK raises an error."""
        category = alchemy_category_factory.build(pk=None).as_hamster(alchemy_store)
        with pytest.raises(ValueError):
            alchemy_store.categories._update(category)

    def test_update_invalid_pk(self, alchemy_store, alchemy_category_factory):
        """
        Make sure that passing a category with a non existing PK raises an error.
        """
        category = alchemy_category_factory().as_hamster(alchemy_store)
        category.pk = category.pk + 10
        with pytest.raises(KeyError):
            alchemy_store.categories._update(category)

    def test_update_existing_name(self, alchemy_store, alchemy_category_factory):
        """
        Make sure that renaming a given alchemy_category to a taken name
        throws an error.
        """
        category_1, category_2 = (
            alchemy_category_factory(), alchemy_category_factory(),
        )
        category_2 = category_2.as_hamster(alchemy_store)
        category_2.name = category_1.name
        with pytest.raises(ValueError):
            alchemy_store.categories._update(category_2)

    def test_remove(self, alchemy_store, alchemy_category_factory):
        """Make sure passing a valid alchemy_category removes it from the db."""
        alchemy_category = alchemy_category_factory()
        category = alchemy_category.as_hamster(alchemy_store)
        result = alchemy_store.categories.remove(category)
        assert result is None
        assert alchemy_store.session.query(AlchemyCategory).get(category.pk) is None

    def test_remove_no_pk(self, alchemy_store, alchemy_category_factory):
        """Ensure that passing a alchemy_category without an PK raises an error."""
        category = alchemy_category_factory.build(pk=None).as_hamster(alchemy_store)
        with pytest.raises(ValueError):
            alchemy_store.categories.remove(category)

    def test_remove_invalid_pk(self, alchemy_store, alchemy_category_factory):
        """Ensure that passing a alchemy_category without an PK raises an error."""
        category = alchemy_category_factory.build(pk=800).as_hamster(alchemy_store)
        with pytest.raises(KeyError):
            alchemy_store.categories.remove(category)

    def test_get_existing_pk(self, alchemy_store, alchemy_category_factory):
        """Make sure method retrieves corresponding object."""
        category = alchemy_category_factory().as_hamster(alchemy_store)
        result = alchemy_store.categories.get(category.pk)
        assert result == category

    def test_get_non_existing_pk(self, alchemy_store, alchemy_category_factory):
        """Make sure we throw an error if PK can not be resolved."""
        alchemy_store.session.query(AlchemyCategory).count == 0
        category = alchemy_category_factory()
        alchemy_store.session.query(AlchemyCategory).count == 1
        with pytest.raises(KeyError):
            alchemy_store.categories.get(category.pk + 1)

    def test_get_by_name(self, alchemy_category_factory, alchemy_store):
        """Make sure a alchemy_category can be retrieved by name."""
        category = alchemy_category_factory().as_hamster(alchemy_store)
        result = alchemy_store.categories.get_by_name(category.name)
        assert result == category

    def test_get_all(self, alchemy_store, set_of_categories):
        result = alchemy_store.categories.get_all()
        assert len(result) == len(set_of_categories)
        assert len(result) == alchemy_store.session.query(AlchemyCategory).count()
        for category in set_of_categories:
            assert category.as_hamster(alchemy_store) in result

    # Test convenience methods.
    def test_get_or_create_get(self, alchemy_store, alchemy_category_factory):
        """
        Test that if we pass a alchemy_category of existing name, we just
        return it.
        """
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        category = alchemy_category_factory().as_hamster(alchemy_store)
        result = alchemy_store.categories.get_or_create(category)
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        assert result == category

    def test_get_or_create_new_name(self, alchemy_store, alchemy_category_factory):
        """
        Make sure that passing a category with new name creates and returns
        new instance.
        """
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        category = alchemy_category_factory.build().as_hamster(alchemy_store)
        category.pk = None
        result = alchemy_store.categories.get_or_create(category)
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        assert result.equal_fields(category)


class TestActivityManager():
    def test_get_or_create_get(self, alchemy_store, alchemy_activity):
        """
        Make sure that passing an existing activity retrieves the corresponding
        instance.

        Note:
            * The activity will is be looked up by its composite key, so not to
            make any assumptions on the existence of a PK.
        """
        activity = alchemy_activity.as_hamster(alchemy_store)
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        result = alchemy_store.activities.get_or_create(activity)
        assert result == activity
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 1

    def test_get_or_create_new(self, alchemy_store, activity):
        """
        Make sure that passing a new activity create a new persitent instance.

        Note:
            * The activity will is be looked up by its composite key, so not to
            make any assumptions on the existence of a PK.
        """
        assert alchemy_store.session.query(AlchemyActivity).count() == 0
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        result = alchemy_store.activities.get_or_create(activity)
        assert result.equal_fields(activity)
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 1

    def test_save_new(self, activity, alchemy_store):
        """Make sure that saving a new activity add a new persistent instance."""
        # [TODO]
        # This should not be needed as ``save`` is a basestore method.
        # Its just a case of 'better save than sorry.
        assert activity.pk is None
        count_before = alchemy_store.session.query(AlchemyActivity).count()
        result = alchemy_store.activities._add(activity)
        count_after = alchemy_store.session.query(AlchemyActivity).count()
        assert count_before < count_after
        assert result.equal_fields(activity)

    def test_save_existing(
        self, alchemy_store, alchemy_activity, alchemy_category_factory,
    ):
        """
        Make sure that saving an existing activity add no new persistent
        instance.
        """
        # [TODO]
        # This should not be needed as ``save`` is a basestore method.
        activity = alchemy_activity.as_hamster(alchemy_store)
        activity.category = alchemy_category_factory()
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 2
        result = alchemy_store.activities.save(activity)
        assert result == activity
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 2

    def test_activity_without_category(self, alchemy_store, activity):
        """Add a new activity without an category."""
        activity.category = None
        result = alchemy_store.activities._add(activity)
        assert result.equal_fields(activity)

    def test_add_new_with_new_category(self, alchemy_store, activity, category):
        """
        Test that adding a new alchemy_activity with new alchemy_category
        creates both.
        """
        assert alchemy_store.session.query(AlchemyActivity).count() == 0
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        activity.category = category
        result = alchemy_store.activities._add(activity)
        db_instance = alchemy_store.session.query(AlchemyActivity).get(result.pk)
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        assert db_instance.as_hamster(alchemy_store).equal_fields(activity)

    def test_add_new_with_existing_category(
        self, alchemy_store, activity, alchemy_category,
    ):
        """
        Test that adding a new activity with existing category does not
        create a new one.
        """
        activity.category = alchemy_category.as_hamster(alchemy_store)
        assert alchemy_store.session.query(AlchemyActivity).count() == 0
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        result = alchemy_store.activities._add(activity)
        db_instance = alchemy_store.session.query(AlchemyActivity).get(result.pk)
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        assert db_instance.as_hamster(alchemy_store).equal_fields(activity)

    def test_add_new_with_existing_name_and_alchemy_category(
        self, alchemy_store, activity, alchemy_activity,
    ):
        """
        Test that adding a new alchemy_activity_with_existing_composite_key
        throws error.
        """
        activity.name = alchemy_activity.name
        activity.category = alchemy_activity.category.as_hamster(alchemy_store)
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        with pytest.raises(ValueError):
            alchemy_store.activities._add(activity)
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 1

    def test_add_with_pk(self, alchemy_store, activity):
        """Make sure that adding an alchemy_activity with a PK raises error."""
        activity.pk = 234
        with pytest.raises(ValueError):
            alchemy_store.activities._add(activity)

    def test_update_without_pk(self, alchemy_store, activity):
        """Make sure that calling update without a PK raises exception."""
        with pytest.raises(ValueError):
            alchemy_store.activities._update(activity)

    def test_update_with_existing_name_and_existing_category_name(
        self, alchemy_store, activity, alchemy_activity, alchemy_category_factory,
    ):
        """
        Make sure that calling update with a taken composite key raises
        exception.
        """
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        category = alchemy_category_factory()
        assert alchemy_activity.category != category
        activity.name = alchemy_activity.name
        assert activity.category.pk is None
        activity.category.name = category.name
        with pytest.raises(ValueError):
            alchemy_store.activities._update(activity)

    def test_update_with_existing_category(
        self, alchemy_store, alchemy_activity, alchemy_category_factory,
    ):
        """
        Test that updateting an activity with existing category does not
        create a new one.
        """
        activity = alchemy_activity.as_hamster(alchemy_store)
        category = alchemy_category_factory().as_hamster(alchemy_store)
        assert alchemy_activity.category != category
        activity.category = category
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 2
        result = alchemy_store.activities._update(activity)
        db_instance = alchemy_store.session.query(AlchemyActivity).get(result.pk)
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert alchemy_store.session.query(AlchemyCategory).count() == 2
        assert db_instance.as_hamster(alchemy_store).equal_fields(activity)

    def test_update_name(
        self, alchemy_store, alchemy_activity, name_string_valid_parametrized,
    ):
        """Test updateing an activities name with a valid new string."""
        activity = alchemy_activity.as_hamster(alchemy_store)
        activity.name = name_string_valid_parametrized
        result = alchemy_store.activities._update(activity)
        db_instance = alchemy_store.session.query(AlchemyActivity).get(result.pk)
        assert db_instance.as_hamster(alchemy_store).equal_fields(activity)

    def test_remove_existing(self, alchemy_store, alchemy_activity):
        """Make sure removing an existsing alchemy_activity works as intended."""
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        activity = alchemy_activity.as_hamster(alchemy_store)
        result = alchemy_store.activities.remove(activity)
        assert alchemy_store.session.query(AlchemyActivity).count() == 0
        assert result is True

    def test_remove_no_pk(self, alchemy_store, activity):
        """
        Make sure that trying to remove an alchemy_activity without a PK
        raises error.
        """
        with pytest.raises(ValueError):
            alchemy_store.activities.remove(activity)

    def test_remove_invalid_pk(self, alchemy_store, alchemy_activity):
        """Test that removing of a non-existent key raises error."""
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        activity = alchemy_activity.as_hamster(alchemy_store)
        activity.pk = activity.pk + 1
        with pytest.raises(KeyError):
            alchemy_store.activities.remove(activity)
        assert alchemy_store.session.query(AlchemyActivity).count() == 1

    def test_get_existing(self, alchemy_store, alchemy_activity):
        """
        Make sure that retrieving an existing alchemy_activity by pk works
        as intended.
        """
        result = alchemy_store.activities.get(alchemy_activity.pk)
        assert result == alchemy_activity.as_hamster(alchemy_store)
        assert result is not alchemy_activity

    def test_get_existing_raw(self, alchemy_store, alchemy_activity):
        """
        Make sure that retrieving an existing alchemy_activity by pk works
        as intended.
        """
        result = alchemy_store.activities.get(alchemy_activity.pk, raw=True)
        assert result == alchemy_activity
        assert result is alchemy_activity

    # FIXME: Add deleted/hidden tests...
    # FIXME: Split this file into one file for each item type.
    def test_get_existing_deleted_false(self, alchemy_store, alchemy_activity):
        """
        Make sure that retrieving an existing alchemy_activity by
        deleted=False works as intended.
        """
        result = alchemy_store.activities.get(alchemy_activity.pk, deleted=False)
        assert result == alchemy_activity.as_hamster(alchemy_store)
        assert result is not alchemy_activity

    def test_get_existing_deleted_true(self, alchemy_store, alchemy_activity_deleted):
        """
        Make sure that retrieving an existing alchemy_activity by
        deleted=True works as intended.
        """
        result = alchemy_store.activities.get(alchemy_activity_deleted.pk, deleted=True)
        assert result == alchemy_activity_deleted.as_hamster(alchemy_store)
        assert result is not alchemy_activity_deleted

    def test_get_non_existing(self, alchemy_store):
        """Make sure quering for a non existent PK raises error."""
        with pytest.raises(KeyError):
            alchemy_store.activities.get(4)

    @pytest.mark.parametrize('raw', (True, False))
    def test_get_by_composite_valid(self, alchemy_store, alchemy_activity, raw):
        """Make sure that querying for a valid name/alchemy_category combo succeeds."""
        activity = alchemy_activity.as_hamster(alchemy_store)
        result = alchemy_store.activities.get_by_composite(
            activity.name,
            activity.category,
            raw=raw,
        )
        if raw:
            assert result == alchemy_activity
            assert result is alchemy_activity
        else:
            assert result == alchemy_activity
            assert result is not alchemy_activity

    def test_get_by_composite_invalid_category(
        self, alchemy_store, alchemy_activity, alchemy_category_factory,
    ):
        """Make sure that querying with an invalid category raises errror."""
        activity = alchemy_activity.as_hamster(alchemy_store)
        category = alchemy_category_factory().as_hamster(alchemy_store)
        with pytest.raises(KeyError):
            alchemy_store.activities.get_by_composite(activity.name, category)

    def test_get_by_composite_invalid_name(
        self, alchemy_store, alchemy_activity, name_string_valid_parametrized,
    ):
        """Make sure that querying with an invalid alchemy_category raises errror."""
        activity = alchemy_activity.as_hamster(alchemy_store)
        invalid_name = activity.name + 'foobar'
        with pytest.raises(KeyError):
            alchemy_store.activities.get_by_composite(invalid_name, activity.category)

    def test_get_all_without_category(self, alchemy_store, alchemy_activity):
        """Make sure method returns all activities."""
        result = alchemy_store.activities.get_all()
        assert len(result) == 1

    def test_get_all_with_category_none(
        self, alchemy_store, alchemy_activity, alchemy_activity_factory,
    ):
        """Make sure only activities without a category are are returned."""
        # FIXME: Do we care about _activity? result ==/is _activity ?
        #   activity = alchemy_activity_factory(category=None)
        alchemy_activity_factory(category=None)
        result = alchemy_store.activities.get_all(category=alchemy_activity.category)
        assert len(result) == 1

    def test_get_all_with_category(self, alchemy_store, alchemy_activity):
        """
        Make sure that activities matching the given alchemy_category are returned.
        """
        activity = alchemy_activity.as_hamster(alchemy_store)
        result = alchemy_store.activities.get_all(category=activity.category)
        assert len(result) == 1

    def test_get_all_with_search_term(self, alchemy_store, alchemy_activity):
        """
        Make sure that activities matching the given term ass name are returned.
        """
        activity = alchemy_activity.as_hamster(alchemy_store)
        result = alchemy_store.activities.get_all(
            category=activity.category,
            search_term=activity.name,
        )
        assert len(result) == 1


class TestTagManager():
    def test_add_new(self, alchemy_store, alchemy_tag_factory):
        """
        Our manager methods return the persistant instance as hamster objects.
        As we want to make sure that we compare our expectations against the
        raw saved object, we look it up explicitly again.
        """
        assert alchemy_store.session.query(AlchemyTag).count() == 0
        tag = alchemy_tag_factory.build().as_hamster(alchemy_store)
        tag.pk = None
        assert alchemy_store.session.query(AlchemyTag).count() == 0
        result = alchemy_store.tags._add(tag)
        assert alchemy_store.session.query(AlchemyTag).count() == 1
        db_instance = alchemy_store.session.query(AlchemyTag).get(result.pk)
        assert tag.equal_fields(db_instance)
        assert tag != db_instance

    def test_add_existing_name(self, alchemy_store, alchemy_tag_factory):
        """
        Make sure that adding a tag with a name that is already present
        gives an error.
        """
        existing_tag = alchemy_tag_factory()
        tag = alchemy_tag_factory.build().as_hamster(alchemy_store)
        tag.name = existing_tag.name
        tag.pk = None
        with pytest.raises(ValueError):
            alchemy_store.tags._add(tag)

    def test_add_with_pk(self, alchemy_store, alchemy_tag_factory):
        """
        Make sure that adding a alchemy_tag that already got an PK raises
        an exception.
        """
        tag = alchemy_tag_factory().as_hamster(alchemy_store)
        tag.name += 'foobar'
        assert tag.pk
        with pytest.raises(ValueError):
            alchemy_store.tags._add(tag)

    def test_update(self, alchemy_store, alchemy_tag_factory, new_tag_values):
        """Test that updateing a alchemy_tag works as expected."""
        alchemy_store.session.query(AlchemyTag).count() == 0
        tag = alchemy_tag_factory().as_hamster(alchemy_store)
        new_values = new_tag_values(tag)
        for key, value in new_values.items():
            assert getattr(tag, key) != value
        for key, value in new_values.items():
            setattr(tag, key, value)
        alchemy_store.tags._update(tag)
        db_instance = alchemy_store.session.query(AlchemyTag).get(tag.pk)
        assert alchemy_store.session.query(AlchemyTag).count() == 1
        assert tag.equal_fields(db_instance)

    def test_update_without_pk(self, alchemy_store, alchemy_tag_factory):
        """Make sure that passing a tag without a PK raises an error."""
        tag = alchemy_tag_factory.build(pk=None).as_hamster(alchemy_store)
        with pytest.raises(ValueError):
            alchemy_store.tags._update(tag)

    def test_update_invalid_pk(self, alchemy_store, alchemy_tag_factory):
        """Make sure that passing a tag with a non existing PK raises an error."""
        tag = alchemy_tag_factory().as_hamster(alchemy_store)
        tag.pk = tag.pk + 10
        with pytest.raises(KeyError):
            alchemy_store.tags._update(tag)

    def test_update_existing_name(self, alchemy_store, alchemy_tag_factory):
        """
        Make sure that renaming a given alchemy_tag to a taken name throws an error.
        """
        tag_1, tag_2 = (alchemy_tag_factory(), alchemy_tag_factory())
        tag_2 = tag_2.as_hamster(alchemy_store)
        tag_2.name = tag_1.name
        with pytest.raises(ValueError):
            alchemy_store.tags._update(tag_2)

    def test_remove(self, alchemy_store, alchemy_tag_factory):
        """Make sure passing a valid alchemy_tag removes it from the db."""
        tag = alchemy_tag_factory().as_hamster(alchemy_store)
        result = alchemy_store.tags.remove(tag)
        assert result is None
        assert alchemy_store.session.query(AlchemyTag).get(tag.pk) is None

    def test_remove_no_pk(self, alchemy_store, alchemy_tag_factory):
        """Ensure that passing a alchemy_tag without an PK raises an error."""
        tag = alchemy_tag_factory.build(pk=None).as_hamster(alchemy_store)
        with pytest.raises(ValueError):
            alchemy_store.tags.remove(tag)

    def test_remove_invalid_pk(self, alchemy_store, alchemy_tag_factory):
        """Ensure that passing a alchemy_tag without an PK raises an error."""
        tag = alchemy_tag_factory.build(pk=800).as_hamster(alchemy_store)
        with pytest.raises(KeyError):
            alchemy_store.tags.remove(tag)

    def test_get_existing_pk(self, alchemy_store, alchemy_tag_factory):
        """Make sure method retrieves corresponding object."""
        tag = alchemy_tag_factory().as_hamster(alchemy_store)
        result = alchemy_store.tags.get(tag.pk)
        assert result == tag

    def test_get_non_existing_pk(self, alchemy_store, alchemy_tag_factory):
        """Make sure we throw an error if PK can not be resolved."""
        alchemy_store.session.query(AlchemyTag).count == 0
        tag = alchemy_tag_factory()
        alchemy_store.session.query(AlchemyTag).count == 1
        with pytest.raises(KeyError):
            alchemy_store.tags.get(tag.pk + 1)

    def test_get_by_name(self, alchemy_tag_factory, alchemy_store):
        """Make sure a alchemy_tag can be retrieved by name."""
        tag = alchemy_tag_factory().as_hamster(alchemy_store)
        result = alchemy_store.tags.get_by_name(tag.name)
        assert result == tag

    def test_get_all(self, alchemy_store, set_of_tags):
        result = alchemy_store.tags.get_all()
        assert len(result) == len(set_of_tags)
        assert len(result) == alchemy_store.session.query(AlchemyTag).count()
        for tag in set_of_tags:
            assert tag.as_hamster(alchemy_store) in result

    # Test convenience methods.
    def test_get_or_create_get(self, alchemy_store, alchemy_tag_factory):
        """
        Test that if we pass a alchemy_tag of existing name, we just return it.
        """
        assert alchemy_store.session.query(AlchemyTag).count() == 0
        tag = alchemy_tag_factory().as_hamster(alchemy_store)
        result = alchemy_store.tags.get_or_create(tag)
        assert alchemy_store.session.query(AlchemyTag).count() == 1
        assert result == tag

    def test_get_or_create_new_name(self, alchemy_store, alchemy_tag_factory):
        """
        Make sure that passing a tag with new name creates and returns new instance.
        """
        assert alchemy_store.session.query(AlchemyTag).count() == 0
        tag = alchemy_tag_factory.build().as_hamster(alchemy_store)
        tag.pk = None
        result = alchemy_store.tags.get_or_create(tag)
        assert alchemy_store.session.query(AlchemyTag).count() == 1
        assert result.equal_fields(tag)


class TestFactManager():
    def test_timeframe_available_existing_fact_overlaps_start_only(
        self, alchemy_store, fact, alchemy_fact,
    ):
        """
        Make sure that passing a fact with only start overlapping an existing
        one raises error.
        """
        fact.start = alchemy_fact.start - datetime.timedelta(days=4)
        fact.end = alchemy_fact.start + datetime.timedelta(minutes=15)
        with pytest.raises(ValueError):
            alchemy_store.facts._add(fact)

    def test_timeframe_available_existing_fact_overlaps_end_only(
        self, alchemy_store, fact, alchemy_fact,
    ):
        """
        Make sure that passing a fact with only end overlapping an existing
        one raises error.
        """
        fact.start = alchemy_fact.end - datetime.timedelta(minutes=1)
        fact.end = alchemy_fact.end + datetime.timedelta(minutes=15)
        with pytest.raises(ValueError):
            alchemy_store.facts._add(fact)

    # Testcase for Bug LIB-253
    def test_timeframe_available_fact_completely_within_existing_timeframe(
        self, alchemy_store, fact, alchemy_fact,
    ):
        """
        Make sure that passing a fact that is completely within an existing
        ones raises error.
        """
        fact.start = alchemy_fact.start + datetime.timedelta(minutes=1)
        fact.end = alchemy_fact.end - datetime.timedelta(minutes=1)
        with pytest.raises(ValueError):
            alchemy_store.facts._add(fact)

    def test_timeframe_available_existing_fact_completly_spans_existing_timeframe(
        self, alchemy_store, fact, alchemy_fact,
    ):
        """
        Make sure that passing a fact that completely spans an existing fact
        raises an error.
        """
        fact.start = alchemy_fact.start - datetime.timedelta(minutes=1)
        fact.end = alchemy_fact.end + datetime.timedelta(minutes=15)
        with pytest.raises(ValueError):
            alchemy_store.facts._add(fact)

    def test_add_tags(self, alchemy_store, fact):
        """Make sure that adding a new valid fact will also save its tags."""
        result = alchemy_store.facts._add(fact)
        assert fact.tags
        db_instance = alchemy_store.session.query(AlchemyFact).get(result.pk)
        assert db_instance.tags
        assert db_instance.as_hamster(alchemy_store).equal_fields(fact)

    def test_add_new_valid_fact_new_activity(self, alchemy_store, fact):
        """
        Make sure that adding a new valid fact with a new activity works as
        intended.
        """
        assert alchemy_store.session.query(AlchemyFact).count() == 0
        assert alchemy_store.session.query(AlchemyActivity).count() == 0
        result = alchemy_store.facts._add(fact)
        db_instance = alchemy_store.session.query(AlchemyFact).get(result.pk)
        assert alchemy_store.session.query(AlchemyFact).count() == 1
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert db_instance.as_hamster(alchemy_store).equal_fields(fact)

    def test_add_new_valid_fact_existing_activity(
        self, alchemy_store, fact, alchemy_activity,
    ):
        """
        Make sure that adding a new valid fact with an existing activity works
        as intended.
        """
        fact.activity = alchemy_activity.as_hamster(alchemy_store)
        assert alchemy_store.session.query(AlchemyFact).count() == 0
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        result = alchemy_store.facts._add(fact)
        db_instance = alchemy_store.session.query(AlchemyFact).get(result.pk)
        assert alchemy_store.session.query(AlchemyFact).count() == 1
        assert alchemy_store.session.query(AlchemyActivity).count() == 1
        assert db_instance.as_hamster(alchemy_store).equal_fields(fact)

    def test_add_with_pk(self, alchemy_store, fact):
        """Make sure that passing a fact with a PK raises error."""
        fact.pk = 101
        with pytest.raises(ValueError):
            alchemy_store.facts._add(fact)

    def test_update_respects_tags(self, alchemy_store, alchemy_fact, new_fact_values):
        """Make sure that updating sets tags as expected."""
        fact = alchemy_fact.as_hamster(alchemy_store)
        new_values = new_fact_values(fact)
        fact.tags = new_values['tags']
        result = alchemy_store.facts._update(fact)
        # Because split_from, fact will have been marked deleted.
        assert fact.deleted
        # And the new Fact will have a larger PK.
        # (lb): We really don't need to impose a strictly increasing order
        # property on the PK, but it's how our code happens to work, so might
        # as well check it.
        assert result.pk > fact.pk
        fact.deleted = False
        assert result.split_from.pk == fact.pk
        # Note that the split-from is not the same because it contains previous tags.
        assert result.split_from != fact
        db_instance = alchemy_store.session.query(AlchemyFact).get(result.pk)
        assert db_instance.as_hamster(alchemy_store).equal_fields(result)
        result.split_from = None
        assert result.equal_fields(fact)

    def test_update_nonexisting_fact(self, alchemy_store, alchemy_fact, new_fact_values):
        """Make sure that trying to update a fact that does not exist raises error."""
        fact = alchemy_fact.as_hamster(alchemy_store)
        new_values = new_fact_values(fact)
        fact.start = new_values['start']
        fact.end = new_values['end']
        fact.pk += 100
        with pytest.raises(KeyError):
            alchemy_store.facts._update(fact)

    def test_update_new_fact(self, alchemy_store, alchemy_fact, new_fact_values):
        """Make sure that trying to update a new fact ,e.g. one without a pk."""
        fact = alchemy_fact.as_hamster(alchemy_store)
        new_values = new_fact_values(fact)
        fact.start = new_values['start']
        fact.end = new_values['end']
        fact.pk = None
        with pytest.raises(ValueError):
            alchemy_store.facts._update(fact)

    def test_save_new(self, fact, alchemy_store):
        count_before = alchemy_store.session.query(AlchemyFact).count()
        result = alchemy_store.facts.save(fact)
        count_after = alchemy_store.session.query(AlchemyFact).count()
        assert count_before < count_after
        assert result.activity.name == fact.activity.name
        assert result.description == fact.description

    def test_remove(self, alchemy_store, alchemy_fact):
        """Make sure the fact but not its tags are removed."""
        count_before = alchemy_store.session.query(AlchemyFact).count()
        tags_before = alchemy_store.session.query(AlchemyTag).count()
        fact = alchemy_fact.as_hamster(alchemy_store)
        result = alchemy_store.facts.remove(fact, purge=True)
        count_after = alchemy_store.session.query(AlchemyFact).count()
        assert count_after < count_before
        assert result is True
        assert alchemy_store.session.query(AlchemyFact).get(fact.pk) is None
        assert alchemy_store.session.query(AlchemyTag).count() == tags_before

    def test_get(self, alchemy_store, alchemy_fact):
        fact = alchemy_fact.as_hamster(alchemy_store)
        result = alchemy_store.facts.get(fact.pk)
        assert result == fact

    def test_get_all(self, set_of_alchemy_facts, alchemy_store):
        result = alchemy_store.facts._get_all()
        assert len(result) == len(set_of_alchemy_facts)
        assert len(result) == alchemy_store.session.query(AlchemyFact).count()

    @pytest.mark.parametrize(('start_filter', 'end_filter'), (
        (10, 12),
        (10, None),
        (None, -12),
    ))
    def test_get_all_existing_facts_not_in_timerange(
        self,
        alchemy_store,
        alchemy_fact,
        bool_value_parametrized,
        start_filter,
        end_filter,
    ):
        """Make sure that a valid timeframe returns an empty list."""
        since, until = None, None
        if start_filter:
            since = alchemy_fact.start + datetime.timedelta(days=start_filter)
        if end_filter:
            until = alchemy_fact.start + datetime.timedelta(days=end_filter)

        result = alchemy_store.facts._get_all(
            since=since, until=until, partial=bool_value_parametrized,
        )
        assert result == []

    @pytest.mark.parametrize(('start_filter', 'end_filter'), (
        (-1, 5),
        (-1, None),
        (None, 5),
        (None, None),
    ))
    def test_get_all_existing_fact_fully_in_timerange(
        self,
        alchemy_store,
        alchemy_fact,
        bool_value_parametrized,
        start_filter,
        end_filter,
    ):
        """Ensure a fact fully within the timeframe is returned."""
        since, until = None, None
        if start_filter:
            since = alchemy_fact.start + datetime.timedelta(days=start_filter)
        if end_filter:
            until = alchemy_fact.start + datetime.timedelta(days=end_filter)

        result = alchemy_store.facts._get_all(
            since=since, until=until, partial=bool_value_parametrized,
        )
        # ANSWER/2018-05-05: (lb): This test is failing. When did it break?
        #   assert result == [alchemy_fact]
        assert len(result) == 1
        assert str(result[0]) == str(alchemy_fact)

    @pytest.mark.parametrize(('start_filter', 'end_filter'), (
        # Fact.start is in timewindow
        (None, 2),
        (-900, 2),
        # Fact.end is in timewindow
        (5, None),
        (5, 900),
    ))
    def test_get_all_existing_fact_partialy_in_timerange(
        self,
        alchemy_store,
        alchemy_fact,
        bool_value_parametrized,
        start_filter,
        end_filter,
    ):
        """
        Test that a fact partially within timeframe is returned with
        ``partial=True`` only.
        """
        since, until = None, None
        if start_filter:
            since = alchemy_fact.start + datetime.timedelta(minutes=start_filter)
        if end_filter:
            until = alchemy_fact.start + datetime.timedelta(minutes=end_filter)
        result = alchemy_store.facts._get_all(
            since=since,
            until=until,
            partial=bool_value_parametrized,
            # 2019-02-14: (lb): When lazy_tags=False, the `result == [alchemy_fact]`
            # fails because result[0].tags != alchemy_fact.tags, because it seems
            # query.all() loads Tag objects with proper PKs, but lazy_tags uses
            # query-coalesce magic to assemble Tag labels without PKs, so PK=None.
            # FIXME/TESTME/2019-02-14: (lb): What's behavior on, say, dob-list?
            #   py.test --pdb -vv \
            #       -k test_get_all_existing_fact_partialy_in_timerange tests/
            lazy_tags=True,
        )
        if bool_value_parametrized:
            assert len(result) == 1
            assert str(result[0]) == str(alchemy_fact)
            assert result == [alchemy_fact]
        else:
            assert result == []

    def test_get_all_search_matches_activity(self, alchemy_store, set_of_alchemy_facts):
        """Make sure facts with ``Fact.activity.name`` matching the term are returned."""
        search_term = set_of_alchemy_facts[1].activity.name
        result = alchemy_store.facts._get_all(search_term=search_term, lazy_tags=True)
        assert len(result) == 1
        assert len(set_of_alchemy_facts) == 5
        assert str(result[0]) == str(set_of_alchemy_facts[1])
        assert result == [set_of_alchemy_facts[1]]

    def test_get_all_search_matches_category(self, alchemy_store, set_of_alchemy_facts):
        """Make sure facts with ``Fact.category.name`` matching the term are returned."""
        search_term = set_of_alchemy_facts[1].category.name
        result = alchemy_store.facts._get_all(search_term=search_term, lazy_tags=True)
        assert len(result) == 1
        assert len(set_of_alchemy_facts) == 5
        assert str(result[0]) == str(set_of_alchemy_facts[1])
        assert result == [set_of_alchemy_facts[1]]

