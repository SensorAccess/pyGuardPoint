import logging
from dataclasses import dataclass
from types import NoneType

log = logging.getLogger(__name__)


@dataclass
class CardholderPersonalDetail:
    email: str
    company: str
    idType: str
    idFreeText: str


@dataclass
class SecurityGroup:
    name: str

@dataclass
class CardholderType:
    typeName: str


@dataclass
class Cardholder:
    uid: str
    lastName: str
    firstName: str
    cardholderIdNumber: str
    status: str
    fromDateValid: str
    isFromDateActive: bool
    toDateValid: str
    isToDateActive: bool
    photo: str
    cardholderType: CardholderType
    securityGroup: SecurityGroup
    cards: list
    cardholderPersonalDetail: CardholderPersonalDetail

    def __init__(self, cardholder_dict: dict):
        for property_name in cardholder_dict:
            # If we have a list - For example, a cardholder has many cards - we only take the first entry
            if isinstance(cardholder_dict[property_name], list):
                setattr(self, property_name, cardholder_dict[property_name])
                '''if len(cardholder_dict[property_name]) > 0:
                    for inner_property in cardholder_dict[property_name][0]:
                        setattr(self, inner_property, cardholder_dict[property_name][0][inner_property])'''

            if isinstance(cardholder_dict[property_name], dict):
                if property_name == "securityGroup":
                    self.securityGroup = SecurityGroup(name=cardholder_dict[property_name]['name'])
                if property_name == "cardholderType":
                    self.cardholderType = CardholderType(typeName=cardholder_dict[property_name]['typeName'])
                if property_name == "cardholderPersonalDetail":
                    self.cardholderPersonalDetail = CardholderPersonalDetail(email=cardholder_dict[property_name]['email'],
                                                                             company=cardholder_dict[property_name]['company'],
                                                                             idType=cardholder_dict[property_name]['idType'],
                                                                             idFreeText=cardholder_dict[property_name]['idFreeText'])

            if isinstance(cardholder_dict[property_name], str):
                setattr(self, property_name, cardholder_dict[property_name])

            if isinstance(cardholder_dict[property_name], NoneType):
                setattr(self, property_name, "None")

            if isinstance(cardholder_dict[property_name], bool):
                setattr(self, property_name, cardholder_dict[property_name])


