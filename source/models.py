from enum import Enum
from tortoise import Model
from tortoise.fields import BigIntField, \
    CharField, CharEnumField, BooleanField, ForeignKeyRelation, ForeignKeyField, OnDelete, BinaryField, DatetimeField, \
    ReverseRelation


class Currency(str, Enum):
    dollar = "доллар"
    euro = "евро"
    dirham = "дирхам"
    naira = "найра"
    lira = "лира"
    ruble = "рубль"


class AdvanceReport(Model):
    id = BigIntField(pk=True)
    projects: ReverseRelation['Project']
    documents: ReverseRelation['Document']
    datetime = DatetimeField(index=True)
    sender_chat_id = CharField(max_length=30)
    accountable_person = CharField(max_length=100)
    status = BooleanField(default=False)


class Project(Model):
    id = BigIntField(pk=True)
    advance_report: ForeignKeyRelation['AdvanceReport'] = ForeignKeyField('models.AdvanceReport',
                                                                          on_delete=OnDelete.CASCADE,
                                                                          related_name="projects")
    project_name = CharField(max_length=100)
    comment = CharField(max_length=1000)
    expense = CharField(max_length=100)
    amount = CharField(max_length=30)
    currency = CharEnumField(enum_type=Currency, max_length=10)


class Document(Model):
    id = BigIntField(pk=True)
    advance_report: ForeignKeyRelation['AdvanceReport'] = ForeignKeyField('models.AdvanceReport',
                                                                          on_delete=OnDelete.CASCADE,
                                                                          related_name="documents")
    name = CharField(max_length=100)
    data = BinaryField()
