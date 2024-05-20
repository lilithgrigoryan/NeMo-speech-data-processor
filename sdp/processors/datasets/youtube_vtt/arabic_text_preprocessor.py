import re
import unicodedata

from pyarabic import araby

from sdp.processors.base_processor import BaseParallelProcessor, DataEntry

# arabic letters
HAMZA = "\u0621"
ALEF_MADDA = "\u0622"
ALEF_HAMZA_ABOVE = "\u0623"
WAW_HAMZA = "\u0624"
ALEF_HAMZA_BELOW = "\u0625"
YEH_HAMZA_ABOVE = "\u0626"
ALEF = "\u0627"
BEH = "\u0628"
TEH_MARBUTA = "\u0629"
TEH = "\u062A"
THEH = "\u062B"
JEEM = "\u062C"
HAH = "\u062D"
KHAH = "\u062E"
DAL = "\u062F"
THAL = "\u0630"
REH = "\u0631"
ZAIN = "\u0632"
SEEN = "\u0633"
SHEEN = "\u0634"
SAD = "\u0635"
DAD = "\u0636"
TAH = "\u0637"
ZAH = "\u0638"
AIN = "\u0639"
GHAIN = "\u063A"
FEH = "\u0641"
QAF = "\u0642"
KAF = "\u0643"
LAM = "\u0644"
MEEM = "\u0645"
NOON = "\u0646"
HEH = "\u0647"
WAW = "\u0648"
ALEF_MAKSURA = "\u0649"
YEH = "\u064A"

# harakats (diacritics)
FATHAT = "\u064E"
KASRAH = "\u0650"
DAMMAH = "\u064F"
SUKUN = "\u0652"
SHADDAH = "\u0651"
KASRATAN = "\u064D"
DAMMATAN = "\u064C"
FATHATAN = "\u064B"

# punctuation marks
QUESTION_MARK = "\u061F"
SAMICOLON = "\u061B"
COMMA = "\u060C"


class ArabicTextPreprocessor(BaseParallelProcessor):
    def __init__(
        self,
        input_text_key: str = "text",
        output_text_key: str = "text",
        remove_diacritics: bool = False,
        remove_punctuation: bool = False,
        normalize_dots: bool = False,
        remove_tatweel: bool = False,
        pyarabic_normalize: bool = False,
        reduce_diacritics: bool = False,
        normalize: bool = False,
        apply_canonical_decomposition: bool = False,
        apply_canonical_decomposition_canonical_composition: bool = False,
        apply_compatability_decomposition: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_text_key = input_text_key
        self.output_text_key = output_text_key
        self.output_text_key = output_text_key
        self.remove_diacritics = remove_diacritics
        self.remove_punctuation = remove_punctuation
        self.normalize_dots = normalize_dots
        self.remove_tatweel = remove_tatweel
        self.pyarabic_normalize = pyarabic_normalize
        self.reduce_diacritics = reduce_diacritics
        self.normalize = normalize
        self.apply_canonical_decomposition = apply_canonical_decomposition
        self.apply_canonical_decomposition_canonical_composition = (
            apply_canonical_decomposition_canonical_composition
        )
        self.apply_compatability_decomposition = apply_compatability_decomposition

    def process_dataset_entry(self, data_entry):
        data_entry[self.output_text_key] = self.clean_data(
            data_entry[self.input_text_key]
        )
        return [DataEntry(data=data_entry)]

    # remove diacritics (https://www.quora.com/What-are-the-diacritics-punctuation-marks-in-Arabic-and-how-can-I-learn-them-all)
    # sukun: \u0652 fatha: \u064E
    # damma: \u064F kasra: \u0650
    # fathatan: \u064B  kasratan: \u064D
    # dammatan: \u064C
    # maddah: \u0653    shadda: \u0651
    def _remove_diacritics(self, text):
        text = re.sub(
            r"['\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653']", "", text
        )
        return text

    def _remove_punctuation(self, text):
        text = re.sub(r"['?!:;\-.,؟،؛\u06D4]", "", text)
        return text

    def _remove_extra_spaces(self, text):
        text = re.sub(" +", " ", text)
        return text

    def _remove_empty_lines(self, text):
        lines = text.split("\n")
        return ("\n").join([line for line in lines if len(line) > 1])

    def _normalize_dots(self, text):
        dots_letters = {
            "ب": list("بتثين"),
            "ح": list("جحخ"),
            "د": list("دذ"),
            "ر": list("رز"),
            "س": list("سش"),
            "ص": list("صض"),
            "ط": list("طظ"),
            "ع": list("عغ"),
            "ف": list("فق"),
            "ا": list("اأإئآؤء"),
            "ه": list("ةه"),
        }
        # convert dots_letters dict to letter-to-letter map
        letters_map = dict(
            {
                letter: k
                for k, letters_list in dots_letters.items()
                for letter in letters_list
            }
        )
        normalized_text = text.translate(str.maketrans(letters_map))
        return normalized_text

    def _normalize(self, text):
        text = araby.strip_diacritics(text)
        text = araby.normalize_alef(text)
        text = araby.normalize_ligature(text)
        text = araby.normalize_teh(text)
        text = araby.reduce_tashkeel(text)

        return text

    def _normalize(self, text):
        text = araby.strip_diacritics(text)
        text = araby.normalize_alef(text)
        text = araby.normalize_ligature(text)
        text = araby.normalize_teh(text)
        text = araby.reduce_tashkeel(text)

        return text

    def clean_data(self, text):
        if self.remove_diacritics:
            text = self._remove_diacritics(text)
        if self.remove_tatweel:
            text = re.sub("ـ", "", text)
        if self.normalize_dots:
            text = self._normalize_dots(text)
        if self.remove_punctuation:
            text = self._remove_punctuation(text)
        if self.pyarabic_normalize:
            text = text.strip()
            # text = re.sub("ى", "ي", text)
            # text = re.sub("ؤ", "ء", text)
            # text = re.sub("ئ", "ء", text)
            # text = re.sub("ة", "ه", text)

            # remove repetetions
            # text = re.sub("[إأٱآا]", "ا", text)
            # text = text.replace('وو', 'و')
            # text = text.replace('يي', 'ي')
            # text = text.replace('ييي', 'ي')
            # text = text.replace('اا', 'ا')

            # text = araby.normalize_alef(text)
            text = araby.normalize_ligature(text)
            # text = araby.normalize_teh(text)
            # text = araby.reduce_tashkeel(text)
            # text = araby.strip_diacritics(text)
        if self.normalize:
            text = self._normalize(text)
        if self.reduce_diacritics:
            text = araby.reduce_tashkeel(text)
        if self.apply_canonical_decomposition:
            text = unicodedata.normalize("NFD", text)
        if self.apply_canonical_decomposition_canonical_composition:
            text = unicodedata.normalize("NFC", text)
        if self.apply_compatability_decomposition:
            text = unicodedata.normalize("NFKC", text)

        text = self._remove_extra_spaces(text)
        text = self._remove_empty_lines(text)
        return text
