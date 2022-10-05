import json
import logging
from dataclasses import dataclass, asdict
from types import NoneType

log = logging.getLogger(__name__)


@dataclass
class SecurityGroup:
    ownerSiteUID: str
    uid: str
    name: str
    apiKey: any
    description: str
    isAppliedToVisitor: bool

    def __init__(self, security_group_dict: dict):
        for property_name in security_group_dict:
            if isinstance(security_group_dict[property_name], str):
                setattr(self, property_name, security_group_dict[property_name])

            if isinstance(security_group_dict[property_name], NoneType):
                setattr(self, property_name, None)

            if isinstance(security_group_dict[property_name], bool):
                setattr(self, property_name, bool(security_group_dict[property_name]))

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class CardholderPersonalDetail:
    email: str
    company: str
    idType: str
    idFreeText: str

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


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
    cards: list
    cardholderPersonalDetail: CardholderPersonalDetail
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
                    self.securityGroup = SecurityGroup(cardholder_dict[property_name])
                if property_name == "cardholderType":
                    self.cardholderType = CardholderType(typeName=cardholder_dict[property_name]['typeName'])
                if property_name == "cardholderPersonalDetail":
                    self.cardholderPersonalDetail = CardholderPersonalDetail(
                        email=cardholder_dict[property_name]['email'],
                        company=cardholder_dict[property_name]['company'],
                        idType=cardholder_dict[property_name]['idType'],
                        idFreeText=cardholder_dict[property_name]['idFreeText'])

            if isinstance(cardholder_dict[property_name], str):
                setattr(self, property_name, cardholder_dict[property_name])

            if isinstance(cardholder_dict[property_name], NoneType):
                setattr(self, property_name, None)

            if isinstance(cardholder_dict[property_name], bool):
                setattr(self, property_name, bool(cardholder_dict[property_name]))

    def dict(self):
        ch = {'cardholder': {}}
        for k, v in asdict(self).items():
            if k == 'ownerSiteUID':
                pass
            if isinstance(v, dict):
                ch['cardholder'][k] = v
            elif isinstance(v, bool):
                ch['cardholder'][k] = v
            elif isinstance(v, NoneType):
                ch['cardholder'][k] = None
            else:
                ch['cardholder'][k] = str(v)

        return ch

if __name__ == "__main__":
    cardholdertype = CardholderType(typeName="test")
    print(cardholdertype.typeName)

    '''securityGroup = SecurityGroup(ownerSiteUID="1234",
                                  uid="sdfs", name="test", apiKey="None", description="test", isAppliedToVisitor=False)
    print(securityGroup.name)
    print(securityGroup.uid)'''