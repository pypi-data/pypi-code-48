from google.protobuf.json_format import MessageToJson
from google.api_core.exceptions import NotFound
import google.oauth2.service_account as service_account
from google.cloud import speech_v1p1beta1 as speech

import json
import os

import ftvstt.transcripts as transcripts
import ftvstt.exceptions as exceptions
import ftvstt.transcribers as transcribers


class Google(transcribers.Transcriber):
    def __init__(self):
        super().__init__()
        self.vocList = None
        self.authenticated = False

    rawType = "json"

    def authenticate(self, email, private_key):
        self.authenticated = False
        service_account_info = {
            "client_email": email,
            "type": "service_account",
            "token_uri": "https://oauth2.googleapis.com/token",
            "private_key": private_key}
        try:
            credentials = (service_account
                           .Credentials
                           .from_service_account_info(service_account_info))
            self.__client = speech.SpeechClient(credentials=credentials)
            (self.__client
                 .long_running_recognize(speech.types.RecognitionConfig(),
                                         speech.types.RecognitionAudio()))
        except NotFound:
            self.authenticated = True
        except Exception:
            pass
        return self.authenticated

    def authenticate_with_file(self, credentialsFilePath):
        self.credentialsFilePath = credentialsFilePath

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentialsFilePath
        self.authenticated = False
        self.__client = speech.SpeechClient()
        self.authenticated = True

    def deauthenticate(self):
        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS')
        self.__client = None
        self.credentialsFilePath = None
        self.authenticated = False

    @exceptions.transcribe_error_handler
    def transcribe(
        self,
        inputPath,
        sample_rate_hertz=16000,
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        enable_word_time_offsets=True,
        enable_speaker_diarization=True,
        lang="fr-FR"
    ):
        lang = self._make_language_compatible(lang)
        transcript = transcripts.Transcript()
        transcript.inputPath = inputPath
        transcript.provider = self.__class__

        if not self.authenticated:
            transcript.exception = exceptions.GoogleAuthError()
            transcript.success = False
            return transcript

        with open(transcript.inputPath, 'rb') as inputFile:
            content = inputFile.read()

        audio = speech.types.RecognitionAudio(content=content)

        config = speech.types.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=sample_rate_hertz,
            language_code=lang,
            enable_word_time_offsets=enable_word_time_offsets,
            enable_speaker_diarization=enable_speaker_diarization
            )

        if self.vocList is not None:
            config.speech_contexts.add(phrases=self.vocList)

        transcript.success = True
        try:
            response = self.__client.long_running_recognize(config, audio)
            resultJson = MessageToJson(response.result())
            ascii_json = bytes(resultJson, 'ascii')
            transcript.raw = ascii_json.decode('unicode-escape')

            self.__class__.set_text(transcript)
            self.__class__.set_words(transcript)
        except Exception as e:
            transcript.success = False
            message = "An error has occured during "
            message += "Google Cloud transciption :\n"
            message += str(e)
            transcript.exception = exceptions.GoogleError(message)

        return transcript

    def set_text(transcript):
        data = json.loads(transcript.raw)
        transcript.text = ""
        for result in data['results']:
            if 'transcript' in result['alternatives'][0].keys():
                transcript.text += result['alternatives'][0]['transcript']
        return transcript.text

    def set_words(transcript):
        transcript.words = []
        transcript.speakers = []
        data = json.loads(transcript.raw)

        for word in data['results'][-1]['alternatives'][0]['words']:
            speaker = transcripts.Speaker(int(word['speakerTag']))

            if speaker not in transcript.speakers:
                transcript.speakers.append(speaker)

            new_word = transcripts.Word(
                word['word'],
                startTime=float(word['startTime'][:-1]),
                endTime=float(word['endTime'][:-1]),
                speaker=speaker
            )

            transcript.words.append(new_word)

    def set_vocabulary_file(self, vocabularyFilePath):
        if not self.authenticated:
            self.vocList = None
            raise exceptions.GoogleAuthError()

        with open(vocabularyFilePath) as vocabularyFile:
            self.vocList = vocabularyFile.read().splitlines()

    def _make_language_compatible(self, lang):
        if lang[2] == '-':
            lang = lang[:2].lower() + lang[2:].upper()
        return lang
