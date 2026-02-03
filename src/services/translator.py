from googletrans import Translator
import asyncio

class TranslationService:
    def __init__(self):
        self.translator = Translator()

    def translate(self, text, dest='vi', src='zh-cn'):
        if not text:
            return ""
        try:
            # googletrans 4.0.0-rc1 fixed most issues with the API change
            result = self.translator.translate(text, dest=dest, src=src)
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return text # Fallback to original text on error
