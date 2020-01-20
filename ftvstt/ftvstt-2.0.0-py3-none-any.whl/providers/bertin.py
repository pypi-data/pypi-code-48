import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json

import xml.etree.ElementTree as ET
import os
from time import sleep

import ftvstt.transcripts as transcripts
import ftvstt.exceptions as exceptions
import ftvstt.transcribers as transcribers

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Bertin(transcribers.Transcriber):
    rawType = "xml"

    def __init__(self, apiBaseUrl):
        super().__init__()

        if apiBaseUrl[-1] != '/':
            self.apiBaseUrl = apiBaseUrl + '/'
        else:
            self.apiBaseUrl = apiBaseUrl

        self.__authTokenId = None
        self.__authTokenValue = None
        self.authenticated = False

    def authenticate(self, user, password):
        self.user = user
        self.password = password

        payload = {
            'login': self.user,
            'password': self.password
        }

        logUrl = self.apiBaseUrl + 'auth-tokens'
        rep = requests.post(logUrl, payload, verify=False)
        repDict = json.loads(rep.text)

        self.authenticated = rep.status_code == 201

        if self.authenticated:
            self.__authTokenId = repDict['id']
            self.__authTokenValue = repDict['value']

        return self.authenticated

    def deauthenticate(self):
        self.user = None
        self.password = None

        requests.delete(
            self.apiBaseUrl + "auth-tokens/" + str(self.__authTokenId),
            verify=False
        )

        self.__authTokenId = None
        self.__authTokenValue = None
        self.authenticated = False

    @exceptions.transcribe_error_handler
    def transcribe(self, inputPath, lang="fr-FR"):
        lang = self._make_language_compatible(lang)
        transcript = transcripts.Transcript()
        transcript.inputPath = inputPath
        transcript.provider = self.__class__

        if self.authenticated:
            transcript.exception = exceptions.BertinAuthError()
            transcript.success = False
            return transcript

        inputName = os.path.basename(transcript.inputPath)
        lastDotIndex = inputName.rfind(".")

        # Removing dots inside the name (provoke error in Bertin)
        apiFileName = inputName[:lastDotIndex].replace(".", "_")
        apiFileName += inputName[lastDotIndex:]

        payload = {
            'audioLanguage': lang,
            'apiFileName': apiFileName,
            'deleteResultFilesAfterSuccess': 'false',
            'deleteTmpFilesAfterSuccess': 'true',
            'deleteIfJobFail': 'true',
            'deleteSourceFilesAfterSuccess': 'true',
            'audioType': 'bn',
            'model': '',
            'resultUrl': ''
        }

        headers = {
            'X-Auth-Token': self.__authTokenValue,
            'accept': 'application/json'
        }

        startTranscriptionUrl = self.apiBaseUrl + 'transcriptions/start'
        with open(transcript.inputPath, 'rb') as inputFile:
            repJob = requests.post(
                startTranscriptionUrl,
                files={'apiFile': inputFile},
                headers=headers,
                data=payload,
                verify=False)

        if repJob.status_code != 200:
            message = "Media upload to Bertin failed."
            transcript.exception = exceptions.BertinError(message)
            transcript.success = False
            return transcript

        repJobDict = json.loads(repJob.text)
        jobId = repJobDict["jobId"]
        statusUrl = self.apiBaseUrl + 'transcriptions/status/' + jobId
        repStatus = requests.get(
            statusUrl,
            headers=headers,
            verify=False)

        if repStatus.status_code == 200:
            statusDict = json.loads(repStatus.text)

        while repStatus.status_code != 200 or statusDict['state'] == 1:
            sleep(2)

            repStatus = requests.get(
                statusUrl,
                headers=headers,
                verify=False)

            if repStatus.status_code == 200:
                statusDict = json.loads(repStatus.text)

        sleep(2)
        transcript.success = statusDict['state'] == 3

        if not transcript.success:
            message = "An error has occured "
            message += "during Bertin transciption."
            transcript.exception = exceptions.BertinError(message)
            transcript.success = False
            return transcript

        resultUrl = self.apiBaseUrl
        resultUrl += 'transcriptions/results/'
        resultUrl += jobId
        resultUrl += '/xml'

        repResult = requests.get(
            resultUrl,
            headers=headers,
            verify=False)

        transcript.raw = json.loads(repResult.text)['fileContent']
        self.__class__.set_text(transcript)
        self.__class__.set_words(transcript)

        return transcript

    def set_text(transcript):
        transcript.text = ""
        root = ET.fromstring(transcript.raw)
        Words = root.findall('SegmentList/SpeechSegment/Word')
        for word in Words:
            transcript.text += word.text[1:]
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
                new_word = transcripts.Word(
                    word.text.strip(),
                    startTime=startTime,
                    endTime=startTime + float(word.attrib['dur']),
                    speaker=speaker,
                    confidence=float(word.attrib['conf']))

                transcript.words.append(new_word)
        return transcript.words

    def _make_language_compatible(self, lang):
        if lang.upper() in ["FR-FR", "FRE", "FR"]:
            return "fre"
        elif lang.upper() in ["EN-US", "EN-EN", "ENG", "EN"]:
            return "eng"
        elif len(lang) == 3:
            return lang
        else:
            return "unknown"
