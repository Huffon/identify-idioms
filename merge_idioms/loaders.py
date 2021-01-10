import csv
import pickle
from typing import Generator

from spacy.matcher import Matcher

from cases import IGNORED_CASES, CORRECTION_CASES
from config import SLIDE_TSV_PATH, IDIOM_MATCHER_PKL_PATH


class Loader:
    def __init__(self, path: str):
        self.path = path

    def load(self, *args, **kwargs):
        raise NotImplementedError


class IdiomsLoader(Loader):
    # not to include in the vocabulary
    SEPARATOR = " "
    # the settings for target idioms
    MIN_WC = 3  # aim for the idioms with length greater than 3
    MIN_LENGTH = 14  # aim for the idioms

    def __init__(self):
        super().__init__(path=SLIDE_TSV_PATH)

    def load(self, target_only: bool = True) -> Generator[str, None, None]:
        """

        :param target_only: if set to false, it will load all the idioms.
        :return:
        """
        corrected_idioms = (
            IdiomsLoader.correct_idiom(idiom)
            for idiom in self.idioms()
        )

        if target_only:
            return (
                idiom
                for idiom in corrected_idioms
                if self.is_target(idiom)
            )

        else:
            return corrected_idioms

    def idioms(self) -> Generator[str, None, None]:
        with open(self.path, 'r') as fh:
            slide_tsv = csv.reader(fh, delimiter="\t")
            # skip the  header
            next(slide_tsv)
            for row in slide_tsv:
                yield row[0]

    @classmethod
    def correct_idiom(cls, idiom: str) -> str:
        if idiom in CORRECTION_CASES.keys():
            return CORRECTION_CASES[idiom]
        else:
            return idiom

    @classmethod
    def is_above_min_len(cls, idiom: str) -> bool:
        return len(idiom) >= cls.MIN_LENGTH

    @classmethod
    def is_above_min_wc(cls, idiom: str) -> bool:
        return len(idiom.split(cls.SEPARATOR)) >= cls.MIN_WC

    @classmethod
    def is_hyphenated(cls, idiom: str) -> bool:
        return idiom.find("-") != -1

    @classmethod
    def is_not_ignored(cls, idiom: str) -> bool:
        return idiom not in IGNORED_CASES

    @classmethod
    def is_target(cls, idiom: str) -> bool:
        # if it is either long enough or hyphenated, then I'm using it.
        return cls.is_not_ignored(idiom) and \
               (cls.is_above_min_wc(idiom) or
                cls.is_above_min_len(idiom) or
                cls.is_hyphenated(idiom))


class IdiomMatcherLoader(Loader):
    def __init__(self):
        super().__init__(path=IDIOM_MATCHER_PKL_PATH)

    def load(self, *args, **kwargs) -> Matcher:
        with open(self.path, 'rb') as fh:
            return pickle.loads(fh.read())
