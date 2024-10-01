from pydantic import BaseModel

from pydantic_gql import GqlField


class MyModel(BaseModel):
    field1: str
    field2: int


class NestedModel(BaseModel):
    nested_field: str


class ComplexModel(BaseModel):
    nested: NestedModel
    list_of_nested: list[NestedModel]


def test_gql_field_from_model():
    gql_field = GqlField.from_model(MyModel)
    assert gql_field.name == "MyModel"
    assert len(gql_field.fields) == 2
    assert gql_field.fields[0].name == "field1"
    assert gql_field.fields[1].name == "field2"


def test_gql_field_from_model_with_name():
    gql_field = GqlField.from_model(MyModel, name="CustomName")
    assert gql_field.name == "CustomName"
    assert len(gql_field.fields) == 2
    assert gql_field.fields[0].name == "field1"
    assert gql_field.fields[1].name == "field2"


def test_gql_field_with_arguments():
    args = {"arg1": "value1"}
    gql_field = GqlField.from_model(MyModel, args=args)
    assert gql_field.args == args


def test_fields_of_model():
    fields = GqlField.fields_of_model(MyModel)
    assert len(fields) == 2
    assert fields[0].name == "field1"
    assert fields[1].name == "field2"


def test_from_pydantic_field():
    field_info = MyModel.model_fields["field1"]
    gql_field = GqlField.from_pydantic_field("field1", field_info)
    assert gql_field.name == "field1"
    assert len(gql_field.fields) == 0


def test_complex_model():
    gql_field = GqlField.from_model(ComplexModel)
    assert gql_field.name == "ComplexModel"
    assert len(gql_field.fields) == 2
    assert gql_field.fields[0].name == "nested"
    assert gql_field.fields[1].name == "list_of_nested"
    assert len(gql_field.fields[0].fields) == 1
    assert gql_field.fields[0].fields[0].name == "nested_field"
    assert len(gql_field.fields[1].fields) == 1
    assert gql_field.fields[1].fields[0].name == "nested_field"
