AVAILABLE_REGIONS = {
    "Kanaker_Zeytun_id": 4,
    "Malatia_Sebastia": 14,
    "Arabkir": 3,
    "Erebuni": 13,
    "1-6 Nork district": 10,
    "Charbakh": 9,
    "Nork-Marash": 7,
    "Center": 1,
    "Ajapnyak": 5,
    "Vahagni district": 18,
    "Large Center": 2,
    "Regions": 16,
    "Argavand": 15,
    "Davitashen": 6,
    "Avan, Avan-Arinj": 12,
    "7-9 Nork district": 11,
    "Shengavit": 8,
}

information_ids = {
    "price": 38,
    "total_space": 12,
    "purpose": 44,
    "office": 49,
    "shop": 50,
    "restaurant": 51,
    "others": 52,
    "rooms": 11,
    "condition": 37,
    "not_repaired": 31,
    "medium_condition": 38,
    "fresh_repaired": 39,
    "building_type": 8,
    "stone": 7,
    "panel": 9,
    "new_building": 13,
    "floor": 10,
    "target_destination": 35,
    "for_summer_house": 23,
    "for_commercial": 24,
    "for_house_building": 25,
    "for_agriculture": 26,
    "mixed_construction": 27,
    "industrial": 28,
    "total_square_footage": 22,
    "total_footage_of_the_building": 15,
    "monthly_price": 39,
    "daily_price": 40,
}

information_gathering_format = {
    "region": "region_id",
    "address": "address location",
    "sale": {
        "commercial_property": {
            "price": "number",
            "total_space": "decimal number",
            "purpose_options": "office/shop/Restaurant/others",
        },
        "apartment": {
            "price": "number",
            "Rooms": "number",
            "total_space": "decimal_number",
            "condition_options": "not repaired/medium condition/Fresh repaired",
            "building_type_options": "stone/Panel/New buildings",
            "Floor": "Comma formatted",
        },
        "land": {
            "price": "number",
            "total_space": "decimal number",
            "target_destination_options": "For summer house/For commercial/For house building/For agriculture/Mixed construction/Industrial",
        },
        "house": {
            "price": "number",
            "stores": "number",
            "total_square_footage": "decimal number",
            "total_footage_of_the_building": "decimal number",
            "rooms": "number",
            "condition_options": "Not repaired/Medium condition/Fresh repaired",
        },
    },
    "Rent": {
        "commercial_property": {
            "monthly_price": "number",
            "total_space": "decimal number",
            "purpose_options": "office/shop/restaurant/others",
        },
        "apartment": {
            "day_price": "number",
            "Month_price": "number",
            "rooms": "number",
            "condition_options": "not repaired/medium condition/fresh repaired",
            "build_type_options": "stone/panel/new building",
            "floor": "comma formatted",
        },
        "house": {
            "daily_price": "number",
            "monthly_price": "number",
            "total_square_footage": "decimal number",
            "total_footage_of_the_building": "decimal number",
            "condition_options": "not repaired/medium condition/fresh repaired",
        },
    },
}
