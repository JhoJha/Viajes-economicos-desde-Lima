# scraper/redbus_scraper/config/config.py

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "es-ES,es;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.redbus.pe",
    "referer": "https://www.redbus.pe/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty"
}

COOKIES = {
    "reqOrigin": "NV",  # 🔥 Esta cookie es **clave** para que la API responda bien
}

BODY = {
    "onlyShow": [],
    "dt": [],
    "SeaterType": [],
    "AcType": [],
    "travelsList": [],
    "amtList": [],
    "bpList": [],
    "dpList": [],
    "CampaignFilter": [],
    "rtcBusTypeList": [],
    "at": [],
    "persuasionList": [],
    "bpIdentifier": [],
    "bcf": [],
    "opBusTypeFilterList": []
}