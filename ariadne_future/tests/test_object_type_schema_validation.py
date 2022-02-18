import pytest
from graphql import GraphQLError

from ..deferred_type import DeferredType
from ..object_type import ObjectType


def test_object_type_raises_error_when_declared_without_schema(snapshot):
    with pytest.raises(TypeError) as err:

        class UserType(ObjectType):
            pass

    snapshot.assert_match(err)


def test_object_type_raises_error_when_declared_with_invalid_schema_type(snapshot):
    with pytest.raises(TypeError) as err:

        class UserType(ObjectType):
            __schema__ = True

    snapshot.assert_match(err)


def test_object_type_raises_error_when_declared_with_invalid_schema_str(snapshot):
    with pytest.raises(GraphQLError) as err:

        class UserType(ObjectType):
            __schema__ = "typo User"

    snapshot.assert_match(err)


def test_object_type_raises_error_when_declared_with_invalid_graphql_type_schema(
    snapshot,
):
    with pytest.raises(ValueError) as err:

        class UserType(ObjectType):
            __schema__ = "scalar DateTime"

    snapshot.assert_match(err)


def test_object_type_raises_error_when_declared_with_multiple_types_schema(snapshot):
    with pytest.raises(ValueError) as err:

        class UserType(ObjectType):
            __schema__ = """
            type User

            type Group
            """

    snapshot.assert_match(err)


def test_object_type_raises_error_when_declared_with_empty_type(snapshot):
    with pytest.raises(ValueError) as err:

        class UserType(ObjectType):
            __schema__ = "type User"

    snapshot.assert_match(err)


def test_object_type_verifies_dependency_type_on_declaration(snapshot):
    class GroupType(ObjectType):
        __schema__ = """
        type Group {
            id: ID!
        }
        """

    class UserType(ObjectType):
        __schema__ = """
        type User {
            group: Group
            groups: [Group!]
        }
        """
        __requires__ = [GroupType]


def test_object_type_raises_error_when_declared_without_type_dependency(snapshot):
    with pytest.raises(ValueError) as err:

        class UserType(ObjectType):
            __schema__ = """
            type User {
                group: Group
                groups: [Group!]
            }
            """

    snapshot.assert_match(err)


def test_object_type_verifies_circular_dependency_using_deferred_object_type():
    class GroupType(ObjectType):
        __schema__ = """
        type Group {
            id: ID!
            users: [User]
        }
        """
        __requires__ = [DeferredType("User")]

    class UserType(ObjectType):
        __schema__ = """
        type User {
            group: Group
        }
        """
        __requires__ = [GroupType]


def test_object_type_verifies_extended_dependency():
    class UserType(ObjectType):
        __schema__ = """
        type User {
            id: ID!
        }
        """

    class ExtendUserType(ObjectType):
        __schema__ = """
        extend type User {
            name: String
        }
        """
        __requires__ = [UserType]


def test_object_type_raises_error_when_declared_without_extended_dependency(snapshot):
    with pytest.raises(ValueError) as err:

        class ExtendUserType(ObjectType):
            __schema__ = """
            extend type User {
                name: String
            }
            """

    snapshot.assert_match(err)
