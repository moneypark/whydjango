from django.test import TestCase

from referral_module.utils import ChoiceEnum


class ColorChoice(ChoiceEnum):
    green = 1
    red = 2


class ChoicesEnumTestCase(TestCase):

    def test_choices_classmethod(self):
        assert ColorChoice.choices() == (
            ('green', 1),
            ('red', 2)
        )
        assert ColorChoice.green.value == 1
