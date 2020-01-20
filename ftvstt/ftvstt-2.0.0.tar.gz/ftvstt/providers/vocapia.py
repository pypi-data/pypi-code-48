import requests
import xml.etree.ElementTree as ET

import ftvstt.transcripts as transcripts
import ftvstt.exceptions as exceptions
import ftvstt.transcribers as transcribers


class Vocapia(transcribers.Transcriber):
    rawType = "xml"

    def __init__(self, apiBaseUrl="https://rest1.vocapia.com:8093/voxsigma"):
        super().__init__()

        self.apiBaseUrl = apiBaseUrl
        self.vocabularyFilePath = None

    def __rawType(self):
        return "xml"

    def authenticate(self, user, password):
        self.user = user
        self.password = password
        auth = (self.user, self.password)
        req = requests.post(self.apiBaseUrl, auth=auth)
        self.authenticated = req.status_code == 400
        return self.authenticated

    def deauthenticate(self):
        self.user = None
        self.password = None
        self.authenticated = False

    @exceptions.transcribe_error_handler
    def transcribe(self, inputPath, lang="fr-FR"):
        lang = self._make_language_compatible(lang)
        transcript = transcripts.Transcript()
        transcript.inputPath = inputPath
        transcript.provider = self.__class__

        if not self.authenticated:
            transcript.exception = exceptions.VocapiaAuthError()
            transcript.success = False
            return transcript

        payload = {
            'method': 'vrbs_trans',
            'model': lang
        }
        auth = (self.user, self.password)

        with open(inputPath, 'rb') as inputFile:
            if self.vocabularyFilePath:
                with open(self.vocabularyFilePath, 'rb') as vocabularyFile:
                    files = {
                            'audiofile': inputFile,
                            'vocfile': vocabularyFile
                    }
                    rep = requests.post(
                        self.apiBaseUrl,
                        files=files,
                        auth=auth,
                        data=payload)
            else:
                files = {
                    'audiofile': inputFile
                }
                rep = requests.post(
                    self.apiBaseUrl,
                    files=files,
                    auth=auth,
                    data=payload)

        resultXMLroot = ET.fromstring(rep.text)
        transcript.success = resultXMLroot.tag != 'Error'

        if transcript.success:
            transcript.raw = rep.text
            self.__class__.set_text(transcript)
            self.__class__.set_words(transcript)
        else:
            message = 'Vocapia error '
            message += resultXMLroot.attrib['code']
            message += ' : '
            message += resultXMLroot.text
            transcript.exception = exceptions.VocapiaError(message)

        return transcript

    def set_text(transcript):
        root = ET.fromstring(transcript.raw)
        WordsTag = root.findall('SegmentList/SpeechSegment/Word')
        Words = [word.text for word in WordsTag]
        transcript.text = ""

        escape_chars = ['-', '.', ',', '!', ':', '?']

        for i in range(len(Words)):
            if Words[i][-2] in ['\'', '-']:
                Words[i] = Words[i][:-1]

            if i+1 < len(Words) and Words[i+1][1] in escape_chars:
                Words[i] = Words[i][:-1]

            transcript.text += Words[i][1:]

        return transcript.text

    def set_words(transcript):
        root = ET.fromstring(transcript.raw)
        speakers = root.findall('SpeakerList/Speaker')
        transcript.speakers = []
        for speaker in speakers:
            gender = speaker.attrib['spkid'][0]
            speakerId = int(speaker.attrib['spkid'][2:])
            new_speaker = transcripts.Speaker(speakerId, gender=gender)
            transcript.speakers.append(new_speaker)

        transcript.words = []
        root = ET.fromstring(transcript.raw)
        SpeechSegments = root.findall('SegmentList/SpeechSegment')

        for speechSegment in SpeechSegments:
            gender = speechSegment.attrib['spkid'][0]
            speakerId = int(speechSegment.attrib['spkid'][2:])

            speaker = transcripts.Speaker(speakerId, gender=gender)

            words = list(speechSegment)
            for word in words:
                startTime = float(word.attrib['stime'])

                word = transcripts.Word(
                    word.text.strip(),
                    startTime=startTime,
                    endTime=startTime + float(word.attrib['dur']),
                    speaker=speaker,
                    confidence=float(word.attrib['conf']))

                transcript.words.append(word)
        return transcript.words

    def set_vocabulary_file(self, vocabularyFilePath):
        if not self.authenticated:
            raise exceptions.VocapiaAuthError()

        self.vocabularyFilePath = vocabularyFilePath

    def _make_language_compatible(self, lang):
        if lang.upper() in ["FR-FR", "FRE", "FR"]:
            return "fre"
        elif lang.upper() in ["EN-US", "EN-EN", "ENG", "EN"]:
            return "eng"
        else:
            return lang
