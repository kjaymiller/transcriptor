import typing

class Vocabulary:
    def __init__(self,
            phrase: str,
            sounds_like: typing.Optional[str] = '',
            display_as: typing.Optional[str] = '',
            ipa: typing.Optional[str] = '',
            abbreviation: bool = False,
            ):
    
        if abbreviation and "." not in phrase:
            self.phrase = ''.join([f'{x}.'.upper() for x in phrase])

        if ' ' in phrase:
            self.phrase = '-'.join(phrase.split(' '))

        else:
            self.phrase = phrase

        self.sounds_like = sounds_like

        if abbreviation: # F.B.I. -> FBI
            self.display_as = display_as.replace('.', '').upper()

        else :
            self.display_as = display_as

        self.ipa = ipa

    @property
    def table(self):
        return f'{self.phrase}\t{self.ipa}\t{self.sounds_like}\t{self.display_as}'
