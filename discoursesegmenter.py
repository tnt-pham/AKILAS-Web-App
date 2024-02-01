import requests
import re


class DiscourseSegmenter:
    """Parses and segments text

    Args:
        text (str): A text to be processed.

    Attributes:
        text (str): A text to be processed.
        tree (str): The syntactic tree of the text in a XML format.
        segments (list): A list of text segments (str).
    """
    def __init__(self, text):
        self.text = text
        self.tree = None
        self.segments = None

    def parse_text(self, url="http://85.214.128.188/api/dplp"):
        """Builds syntactic tree from text

        Args:
            url (str): Link to parsing API
        """
        sample = {"text": self.text}
        response = requests.post(url, json=sample)
        self.tree = response.text  # str

    def segment_text(self):
        """Get segments from syntactic tree
        """
        if self.tree is None:
            self.parse_text()
        segment_pattern = r'<segment[^>]*>(.*?)<\/segment>'
        self.segments = re.findall(segment_pattern, self.tree, re.DOTALL)

    def get_segmented_text(self, sep='|'):
        """Puts segments together to a segmented text

        Args:
            sep (str): Separator between segments. Defaults to '|'.

        Returns:
            str: Segmented text.
        """
        if self.segments is None:
            self.segment_text()
        segmented_text = f"{sep} "
        for segment in self.segments:
            segmented_text += f"{segment}{sep}"
        return segmented_text

    def remove_umlaut(self):
        """Replaces German Umlaute with respective alternative
        """
        self.text = self.text.replace("ä", "ae")
        self.text = self.text.replace("ö", "oe")
        self.text = self.text.replace("ü", "ue")
        self.text = self.text.replace("ß", "ss")

    def convert_umlaut(self, text):
        """Corrects representation of characters

        Args:
            text (str): Text where certain characters are corrected.

        Returns:
            str: Text with corrected characters.
        """
        umlaut_dict = {"ß": "&#223;",
                       "ä": "&#228;",
                       "ö": "&#246;",
                       "ü": "&#252;",
                       "<": "&lt;",
                       ">": "&gt;"}
        for umlaut, alternative in umlaut_dict.items():
            text = text.replace(alternative, umlaut)
        return text


if __name__ == '__main__':
    text = "Hier ist ein Text. Bitte segmentieren und mir Bescheid geben."
    ds = DiscourseSegmenter(text)
    print(ds.get_segmented_text())
