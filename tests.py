import whatsanalyse
import datetime

message_1 = "27/09/2018, 23:51 - Sil: Bradford...."
item = whatsanalyse.Item(message_1)


class TestCase(object):
    def test_author_name(self):
        assert item.author_name == "Sil"

    def test_is_comment(self):
        assert item.is_comment
        assert not item.is_audio
        assert not item.is_gif
        assert not item.is_media
        assert not item.is_video

    def test_text(self):
        assert item.text == "Bradford...."

    def test_datetime(self):
        assert item.datetime == datetime.datetime(2018, 9, 27, 23, 51)