import logging
from dataclasses import dataclass, asdict
from enum import Enum

log = logging.getLogger(__name__)


class SortAlgorithm(Enum):
    SERVER_DEFAULT = 0,
    FUZZY_MATCH = 1


@dataclass
class Card:
    technologyType: int = 0
    description: str = ""
    cardCode: str = ""
    status: str = "Free"
    cardholderUID: any = None
    cardType: str = "Magnetic"
    readerFunctionUID: str = ""
    status: str = ""
    uid: str = ""

    def __init__(self, card_dict: dict):
        for property_name in card_dict:
            if isinstance(card_dict[property_name], str):
                setattr(self, property_name, card_dict[property_name])

            if isinstance(card_dict[property_name], type(None)):
                setattr(self, property_name, None)

            if isinstance(card_dict[property_name], bool):
                setattr(self, property_name, bool(card_dict[property_name]))

    def dict(self, editable_only=False):
        c = {}
        for k, v in asdict(self).items():
            if isinstance(v, list):
                c[k] = v
            elif isinstance(v, dict):
                c[k] = v
            elif isinstance(v, bool):
                c[k] = v
            elif isinstance(v, int):
                c[k] = v
            elif isinstance(v, type(None)):
                c[k] = None
            else:
                c[k] = str(v)

        if editable_only:
            if 'uid' in c:
                c.pop('uid')

        return c


@dataclass
class Area:
    uid: str = ""
    name: str = ""

    def __init__(self, area_dict: dict):
        for property_name in area_dict:
            if isinstance(area_dict[property_name], str):
                setattr(self, property_name, area_dict[property_name])

            if isinstance(area_dict[property_name], type(None)):
                setattr(self, property_name, None)

            if isinstance(area_dict[property_name], bool):
                setattr(self, property_name, bool(area_dict[property_name]))

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class SecurityGroup:
    ownerSiteUID: str = ""
    uid: str = ""
    name: str = ""
    apiKey: any = ""
    description: str = ""
    isAppliedToVisitor: bool = False

    def __init__(self, security_group_dict: dict):
        for property_name in security_group_dict:
            if isinstance(security_group_dict[property_name], str):
                setattr(self, property_name, security_group_dict[property_name])

            if isinstance(security_group_dict[property_name], type(None)):
                setattr(self, property_name, None)

            if isinstance(security_group_dict[property_name], bool):
                setattr(self, property_name, bool(security_group_dict[property_name]))

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class CardholderCustomizedField:
    uid: str = ""
    cF_BoolField_1: bool = False,
    cF_BoolField_2: bool = False
    cF_BoolField_3: bool = False
    cF_BoolField_4: bool = False
    cF_BoolField_5: bool = False
    cF_IntField_1: int = 0
    cF_IntField_2: int = 0
    cF_IntField_3: int = 0
    cF_IntField_4: int = 0
    cF_IntField_5: int = 0
    cF_DateTimeField_1: any = None
    cF_DateTimeField_2: any = None
    cF_DateTimeField_3: any = None
    cF_DateTimeField_4: any = None
    cF_DateTimeField_5: any = None
    cF_StringField_1: str = ""
    cF_StringField_2: str = ""
    cF_StringField_3: str = ""
    cF_StringField_4: str = ""
    cF_StringField_5: str = ""
    cF_StringField_6: str = ""
    cF_StringField_7: str = ""
    cF_StringField_8: str = ""
    cF_StringField_9: str = ""
    cF_StringField_10: str = ""
    cF_StringField_11: str = ""
    cF_StringField_12: str = ""
    cF_StringField_13: str = ""
    cF_StringField_14: str = ""
    cF_StringField_15: str = ""
    cF_StringField_16: str = ""
    cF_StringField_17: str = ""
    cF_StringField_18: str = ""
    cF_StringField_19: str = ""
    cF_StringField_20: str = ""

    def __init__(self, custom_fields_dict: dict):
        for property_name in custom_fields_dict:
            if isinstance(custom_fields_dict[property_name], str):
                setattr(self, property_name, custom_fields_dict[property_name])

            if isinstance(custom_fields_dict[property_name], type(None)):
                setattr(self, property_name, None)

            if isinstance(custom_fields_dict[property_name], bool):
                setattr(self, property_name, bool(custom_fields_dict[property_name]))

    def dict(self):
        c = {}
        for k, v in asdict(self).items():
            if isinstance(v, list):
                c[k] = v
            elif isinstance(v, dict):
                c[k] = v
            elif isinstance(v, bool):
                c[k] = v
            elif isinstance(v, int):
                c[k] = v
            elif isinstance(v, type(None)):
                c[k] = None
            else:
                c[k] = str(v)
        return c


@dataclass
class CardholderPersonalDetail:
    email: str
    company: str
    idType: str
    idFreeText: str

    def dict(self):
        ch_pd = {}
        for k, v in asdict(self).items():
            if isinstance(v, list):
                ch_pd[k] = v
            elif isinstance(v, dict):
                ch_pd[k] = v
            elif isinstance(v, bool):
                ch_pd[k] = v
            elif isinstance(v, int):
                ch_pd[k] = v
            elif isinstance(v, type(None)):
                ch_pd[k] = None
            else:
                ch_pd[k] = str(v)

        return ch_pd


@dataclass
class CardholderType:
    typeName: str

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class Cardholder:
    uid: str
    lastName: str
    firstName: str
    cardholderIdNumber: any
    status: str
    fromDateValid: str
    isFromDateActive: bool
    toDateValid: str
    isToDateActive: bool
    photo: any
    cardholderType: CardholderType
    securityGroup: SecurityGroup
    cardholderPersonalDetail: CardholderPersonalDetail
    cardholderCustomizedField: CardholderCustomizedField
    insideArea: Area
    ownerSiteUID: any
    securityGroupApiKey: any
    ownerSiteApiKey: any
    accessGroupApiKeys: any
    liftAccessGroupApiKeys: any
    cardholderTypeUID: any
    departmentUID: any
    description: any
    grantAccessForSupervisor: bool
    isSupervisor: bool
    needEscort: bool
    personalWeeklyProgramUID: any
    pinCode: str
    sharedStatus: str
    securityGroupUID: any
    accessGroupUIDs: any
    liftAccessGroupUIDs: any
    lastDownloadTime: any
    lastInOutArea: any
    lastInOutReaderUID: any
    lastInOutDate: any
    lastAreaReaderDate: any
    lastAreaReaderUID: any
    lastPassDate: any
    lastReaderPassUID: any
    insideAreaUID: any
    cards: list

    def __init__(self, cardholder_dict: dict):
        for property_name in cardholder_dict:
            # If we have a list - For example, a cardholder has many cards - we only take the first entry
            if isinstance(cardholder_dict[property_name], list):
                if property_name == "cards":
                    setattr(self, property_name, [])
                    for card_entry in cardholder_dict[property_name]:
                        self.cards.append(Card(card_entry))
                else:
                    setattr(self, property_name, cardholder_dict[property_name])
                '''if len(cardholder_dict[property_name]) > 0:
                    for inner_property in cardholder_dict[property_name][0]:
                        setattr(self, inner_property, cardholder_dict[property_name][0][inner_property])'''

            if isinstance(cardholder_dict[property_name], dict):
                if property_name == "insideArea":
                    self.insideArea = Area(cardholder_dict[property_name])
                if property_name == "securityGroup":
                    self.securityGroup = SecurityGroup(cardholder_dict[property_name])
                if property_name == "cardholderType":
                    self.cardholderType = CardholderType(typeName=cardholder_dict[property_name]['typeName'])
                if property_name == "cardholderPersonalDetail":
                    self.cardholderPersonalDetail = CardholderPersonalDetail(
                        email=cardholder_dict[property_name]['email'],
                        company=cardholder_dict[property_name]['company'],
                        idType=cardholder_dict[property_name]['idType'],
                        idFreeText=cardholder_dict[property_name]['idFreeText'])
                if property_name == "cardholderCustomizedField":
                    self.cardholderCustomizedField = CardholderCustomizedField(cardholder_dict[property_name])

            if isinstance(cardholder_dict[property_name], str):
                setattr(self, property_name, cardholder_dict[property_name])

            if isinstance(cardholder_dict[property_name], type(None)):
                setattr(self, property_name, None)

            if isinstance(cardholder_dict[property_name], bool):
                setattr(self, property_name, bool(cardholder_dict[property_name]))

    def to_search_pattern(self):
        pattern = ""
        if self.firstName:
            pattern += self.firstName + " "
        if self.lastName:
            pattern += self.lastName + " "
        if self.cardholderPersonalDetail.company:
            pattern += self.cardholderPersonalDetail.company + " "
        if self.cardholderPersonalDetail.email:
            pattern += self.cardholderPersonalDetail.email
        return pattern

    def pretty_print(self, obj: object = None):
        if obj == None:
            obj = self
        for attribute_name in obj.__dict__:
            attribute = getattr(obj, attribute_name)
            if hasattr(attribute, '__dict__'):
                print(f"{attribute_name}:")
                obj.pretty_print(attribute)
            else:
                print(f"\t{attribute_name:<25}" + str(attribute))

    def dict(self, editable_only=False):
        ch = {}
        for k, v in asdict(self).items():
            if isinstance(v, list):
                ch[k] = v
            elif isinstance(v, dict):
                ch[k] = v
            elif isinstance(v, bool):
                ch[k] = v
            elif isinstance(v, type(None)):
                ch[k] = None
            else:
                ch[k] = str(v)

        if editable_only:
            ch = self._remove_non_editable(ch)
        return ch

    @staticmethod
    def _remove_non_editable(ch: dict):
        if 'uid' in ch:
            ch.pop('uid')
        if 'lastDownloadTime' in ch:
            ch.pop('lastDownloadTime')
        if 'lastInOutArea' in ch:
            ch.pop('lastInOutArea')
        if 'lastInOutReaderUID' in ch:
            ch.pop('lastInOutReaderUID')
        if 'lastInOutDate' in ch:
            ch.pop('lastInOutDate')
        if 'lastAreaReaderDate' in ch:
            ch.pop('lastAreaReaderDate')
        if 'lastAreaReaderUID' in ch:
            ch.pop('lastAreaReaderUID')
        if 'lastPassDate' in ch:
            ch.pop('lastPassDate')
        if 'lastReaderPassUID' in ch:
            ch.pop('lastReaderPassUID')
        if 'status' in ch:
            ch.pop('status')
        if 'cardholderPersonalDetail' in ch:
            ch.pop('cardholderPersonalDetail')
        if 'cardholderType' in ch:
            ch.pop('cardholderType')
        if 'securityGroup' in ch:
            ch.pop('securityGroup')
        if 'cards' in ch:
            ch.pop('cards')

        return ch


if __name__ == "__main__":
    cardholdertype = CardholderType(typeName="test")
    print(cardholdertype.typeName)

    '''securityGroup = SecurityGroup(ownerSiteUID="1234",
                                  uid="sdfs", name="test", apiKey="None", description="test", isAppliedToVisitor=False)
    print(securityGroup.name)
    print(securityGroup.uid)'''
