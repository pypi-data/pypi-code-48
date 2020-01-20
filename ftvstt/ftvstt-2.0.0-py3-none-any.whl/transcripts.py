import json


class Transcript:
    def __init__(self, raw=None, provider=None):
        self.exception = None
        self.inputPath = None
        self.provider = None
        self.raw = None
        self.rawType = None
        self.speakers = None
        self.success = None
        self.text = None
        self.words = None

        if provider is not None and raw is not None:
            self.provider = provider
            self.raw = raw
            self.rawType = provider.rawType
            provider.set_text(self)
            provider.set_words(self)
            self.success = True

    def dump_raw_result(self, outputPath):
        if not self.success:
            raise self.exception

        with open(outputPath, 'w') as outputFile:
            outputFile.write(self.raw)

    def dump_text_result(self, outputPath):
        if not self.success:
            raise self.exception

        with open(outputPath, 'w') as outputFile:
            outputFile.write(self.text)

    def to_dict(self):
        if not self.success:
            return

        speakers = [
            speaker.__dict__.copy()
            for speaker in self.__dict__['speakers']
        ]
        words = [
            word.__dict__.copy()
            for word in self.__dict__['words']
        ]

        resDict = {
            "provider": self.__dict__['provider'].__name__,
            "speakers": speakers,
            "text": self.__dict__['text'],
            "words": words
        }

        for i in range(len(resDict['words'])):
            speaker = resDict['words'][i]['speaker']
            if speaker is not None:
                resDict['words'][i]['speakerId'] = speaker.id
            else:
                resDict['words'][i]['speakerId'] = None
            del resDict['words'][i]['speaker']

        return resDict

    def dump_normalised_result(self, outputPath):
        if not self.success:
            return

        content = self.to_dict()
        with open(outputPath, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(content, ensure_ascii=False, indent=4))


class Word:
    def __init__(
        self,
        content,
        startTime=None,
        endTime=None,
        speaker=None,
        confidence=None
    ):
        self.content = content
        self.startTime = startTime
        self.endTime = endTime
        self.speaker = speaker
        self.confidence = confidence


class Speaker:
    def __init__(self, id, gender=None):
        self.id = id
        self.gender = gender

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.__dict__ == other.__dict__
