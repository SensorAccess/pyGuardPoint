import logging, sys
from importlib.metadata import version
from pprint import pprint

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError, GuardPointUnauthorized, SortAlgorithm

#from pyGuardPoint import GuardPoint, GuardPointError

GP_HOST = 'https://sensoraccess.duckdns.org'
#GP_HOST = 'http://192.168.1.111:10695'
GP_USER = 'admin'
GP_PASS = 'admin'
#GP_USER = 'remko'
#GP_PASS = 'remko'
#GP_USER = 'robert'
#GP_PASS = 'password'
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
TLS_P12_PWD = "test"
#SITE_UID = "f342eade-eb43-4359-918d-d067d609fc38" # Sensor Office
#SITE_UID = "90be9b9d-c87f-44b0-9ff9-e0f8725abbad" # Force site filter
#SITE_UID = None

if __name__ == "__main__":
    py_gp_version = version("pyGuardPoint")
    print("pyGuardPoint Version:" + py_gp_version)
    py_gp_version_int = int(py_gp_version.replace('.', ''))
    if py_gp_version_int < 193:
        print("Please Update pyGuardPoint")
        print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
        exit()

    logging.basicConfig(level=logging.DEBUG)
    gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD
                    )

    try:
        url = ("/odata/API_Cardholders?$select=uid,lastName,firstName,cardholderIdNumber,status,fromDateValid,isFromDateActive,toDateValid,isToDateActive,cardholderType,securityGroup,cardholderPersonalDetail,cardholderCustomizedField,insideArea,ownerSiteUID,securityGroupApiKey,ownerSiteApiKey,accessGroupApiKeys,liftAccessGroupApiKeys,cardholderTypeUID,departmentUID,description,grantAccessForSupervisor,isSupervisor,needEscort,personalWeeklyProgramUID,pinCode,sharedStatus,securityGroupUID,accessGroupUIDs,liftAccessGroupUIDs,lastDownloadTime,lastInOutArea,lastInOutReaderUID,lastInOutDate,lastAreaReaderDate,lastAreaReaderUID,lastPassDate,lastReaderPassUID,insideAreaUID,cards&$expand=cardholderType,cards,cardholderPersonalDetail,cardholderCustomizedField,insideArea,securityGroup&"
               ""
               "$filter=((cardholderTypeUID%20eq%2022222222-2222-2222-2222-222222222222)%20and%20((insideAreaUID%20eq%2000000000-0000-0000-0000-100000000001)%20or%20(insideAreaUID%20eq%2000000000-0000-0000-0000-100000000002)%20or%20(insideAreaUID%20eq%2000000000-0000-0000-0000-100000000003)%20or%20(insideAreaUID%20eq%202217bc5a-41be-40f7-9da1-41fcae6c639d)%20or%20(insideAreaUID%20eq%20265f4dd8-5792-49a5-bc9f-ccc01565c2ba)%20or%20(insideAreaUID%20eq%20a498c2b1-2d3e-4501-8210-d246fbae26b4)%20or%20(insideAreaUID%20eq%208fadd0a2-c112-4993-9f79-e9c7237923f9))%20and%20(contains(firstName,'john')%20or%20contains(firstName,'owen')%20or%20contains(firstName,'test')%20or%20contains(lastName,'john')%20or%20contains(lastName,'owen')%20or%20contains(lastName,'test')%20or%20contains(CardholderPersonalDetail/company,'john')%20or%20contains(CardholderPersonalDetail/company,'owen')%20or%20contains(CardholderPersonalDetail/company,'test')%20or%20contains(CardholderPersonalDetail/email,'john')%20or%20contains(CardholderPersonalDetail/email,'owen')%20or%20contains(CardholderPersonalDetail/email,'test')))&$orderby=fromDateValid%20desc&$top=10&$skip=0")
        areas = gp.get_areas()
        a = []
        a.append(areas[0])
        a.append(areas[1])
        a.append(areas[2])
        a.append(areas[3])
        a.append(areas[4])

        cardholders = gp.get_card_holders(count=False,
                                          areas=areas,
                                          #firstName='Remko',
                                          search_terms='r.vanderlaan@schoutentechniek.nl',
                                          sort_algorithm=SortAlgorithm.FUZZY_MATCH,
                                          threshold=65)
        if isinstance(cardholders, int):
            print(cardholders)
        else:
            for cardholder in cardholders:
                print(f"\tFirst Name: {cardholder.firstName}")
                print(f"\tLast Name: {cardholder.lastName}")
                print(f"\tEmail: {cardholder.cardholderPersonalDetail.email}")
            #print(f"\townerSiteUID: {cardholder.ownerSiteUID}")
                print(f"\tCardholderUID: {cardholder.uid}")
                print(f"\tPin Code: {cardholder.pinCode}")
                print(f"\tCompany: {cardholder.cardholderPersonalDetail.company}")
                print(f"\n")
            #print(f"\tStatus: {cardholder.status}")

    except GuardPointError as e:
        print(f"GuardPointError: {e}")
    except Exception as e:
        print(f"Exception: {e}")




