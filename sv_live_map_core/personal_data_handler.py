"""Get data from personal_data"""

import json
from .sv_enums import Ability, Gender, GenderGeneration, Species

class PersonalDataHandler:
    """Get data from personal_data"""
    _personal_data: dict[str, dict] = None
    def __init__(self) -> None:
        with open(
            "./resources/personal_data_partial.json",
            "r",
            encoding = "utf-8"
        ) as personal_data_json:
            if PersonalDataHandler._personal_data is None:
                PersonalDataHandler._personal_data = json.load(personal_data_json)

    @staticmethod
    def get_data(species: Species, form: int) -> dict:
        """Get personal data of a mon"""
        if form is None:
            form = 0
        return PersonalDataHandler._personal_data[f"{species.value}-{form}"]

    @staticmethod
    def fixed_gender(species: Species, form: int) -> GenderGeneration:
        """Return gender generation type of a mon"""
        return GenderGeneration(PersonalDataHandler.get_data(species, form)["gender_group"])

    @staticmethod
    def get_gender(species: Species, form: int, gender_rand: int) -> Gender:
        """Compare a mon's gender rand"""
        return Gender(gender_rand < PersonalDataHandler.get_data(species, form)["gender_ratio"])

    @staticmethod
    def get_ability(species: Species, form: int, ability: int) -> Ability:
        """Get a mon's ability based on its index"""
        return Ability(PersonalDataHandler.get_data(species, form)["abilities"][ability])
