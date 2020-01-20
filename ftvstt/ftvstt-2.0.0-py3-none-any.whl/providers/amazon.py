import boto3
import requests

import time
import os
import json
import csv

import random

import ftvstt.transcripts as transcripts
import ftvstt.exceptions as exceptions
import ftvstt.transcribers as transcribers


class Amazon(transcribers.Transcriber):
    rawType = "json"

    def __init__(self, bucketName, region_name='eu-west-3'):
        super().__init__()
        self.bucketName = bucketName
        self.region_name = region_name
        self.__vocList = None
        self.__vocName = None

    def authenticate_with_file(self, credentialsFilePath):
        self.credentialsFilePath = credentialsFilePath

        auth = {}
        self.authenticated = True
        try:
            with open(self.credentialsFilePath, mode="r") as csvFile:
                reader = csv.reader(csvFile, delimiter="=")
                for line in reader:
                    auth[line[0]] = line[1]

            self.__s3Client = boto3.client(
                's3',
                aws_access_key_id=auth['AWSAccessKeyId'],
                aws_secret_access_key=auth['AWSSecretKey']
            )

            self.__transcribeClient = boto3.client(
                'transcribe',
                region_name=self.region_name,
                aws_access_key_id=auth['AWSAccessKeyId'],
                aws_secret_access_key=auth['AWSSecretKey']
            )

            self.__s3Client.list_buckets()

        except Exception:
            self.authenticated = False

        return self.authenticated

    def authenticate(self, awsAccessKeyId, awsSecretAccessKey):
        self.id = awsAccessKeyId
        self.password = awsSecretAccessKey

        self.authenticated = True
        try:
            self.__s3Client = boto3.client(
                's3',
                aws_access_key_id=self.id,
                aws_secret_access_key=self.password
            )

            self.__transcribeClient = boto3.client(
                'transcribe',
                region_name=self.region_name,
                aws_access_key_id=self.id,
                aws_secret_access_key=self.password
            )

            self.__s3Client.list_buckets()
        except Exception:
            self.authenticated = False

        return self.authenticated

    def deauthenticate(self):
        self.credentialsFilePath = None
        self.id = None
        self.password = None

        self.__s3Client = None
        self.__transcribeClient = None

    @exceptions.transcribe_error_handler
    # set s3file=True if the input file is already on S3,
    # in that case inputPath should be the url of the file
    def transcribe(self, inputPath, lang="fr-FR", s3file=False):
        lang = self._make_language_compatible(lang)
        transcript = transcripts.Transcript()
        transcript.inputPath = inputPath
        transcript.provider = self.__class__

        if not self.authenticated:
            transcript.exception = exceptions.AmazonAuthError()
            transcript.success = False
        if s3file:
            audioUri = inputPath
            transcript.exception = None
        else:
            s3AudioPath = "ftvstt/"
            s3AudioPath = os.path.basename(transcript.inputPath)
            audioUri, transcript.exception = self.__s3_upload(
                transcript.inputPath,
                s3AudioPath
            )

        if transcript.exception:
            transcript.success = False
            return transcript

        jobName = "ftvstt_job_"
        jobName += str(random.randint(1, 1e6))
        jobName += "_"
        jobName += os.path.basename(transcript.inputPath).replace(".", "_")

        settings = {
            'MaxSpeakerLabels': 10,
            'ShowSpeakerLabels': True
        }
        if not self.__vocList:
            settings['VocabularyName'] = self.__vocName

        try:
            self.__transcribeClient.start_transcription_job(
                TranscriptionJobName=jobName,
                Media={'MediaFileUri': audioUri},
                MediaFormat='wav',
                LanguageCode=lang,
                Settings=settings
            )
        except Exception as e:
            message = "Amazon Transcription failed : \n"
            message += str(e)
            transcript.exception = exceptions.AmazonError(message)
            transcript.success = False
            return transcript

        completed, job = self.__wait_for_transcription_job(jobName)

        if not completed:
            transcript.success = False
            message = "Amazon Transcription failed : \n"
            message += job['TranscriptionJob']['FailureReason']
            transcript.exception = exceptions.AmazonError(message)
            return transcript

        rawResultsUri = (job['TranscriptionJob']
                            ['Transcript']
                            ['TranscriptFileUri'])
        rep = requests.get(rawResultsUri)

        transcript.success = rep.status_code != 404

        if not transcript.success:
            message = "Amazon Transcription failed : \n"
            message += "Impossible to reach transcription result at :"
            message += rawResultsUri
            transcript.exception = exceptions.AmazonError(message)
            return transcript

        transcript.raw = rep.text
        self.__class__.set_text(transcript)
        self.__class__.set_words(transcript)

        time.sleep(2)
        self.__transcribeClient.delete_transcription_job(
            TranscriptionJobName=jobName)

        return transcript

    def set_text(transcript):
        data = json.loads(transcript.raw)
        transcript.text = ""
        for result in data['results']['transcripts']:
            transcript.text += result['transcript']
        return transcript.text

    def set_words(transcript):
        transcript.words = []
        transcript.speakers = []

        data = json.loads(transcript.raw)

        segments = data['results']['speaker_labels']['segments']

        for segment in segments:
            speaker_id = int(segment['speaker_label'][4:])
            speaker = transcripts.Speaker(speaker_id)

            if speaker not in transcript.speakers:
                transcript.speakers.append(speaker)

        for word in data['results']['items']:
            content = word['alternatives'][0]['content']

            if word['type'] == "punctuation":
                if transcript.words == []:
                    startTime = endTime = .0
                else:
                    startTime = transcript.words[-1].endTime
                    endTime = startTime
            else:
                startTime = float(word['start_time'])
                endTime = float(word['end_time'])
            confidence = float(word['alternatives'][0]['confidence'])

            speaker = None

            for segment in segments:
                segmentStartTime = float(segment['start_time'])
                segmentEndTime = float(segment['end_time'])
                if startTime >= segmentStartTime and endTime <= segmentEndTime:
                    speakerId = int(segment['speaker_label'][4:])
                    speaker = transcripts.Speaker(speakerId)
                    break

            newWord = transcripts.Word(
                content,
                startTime=startTime,
                endTime=endTime,
                confidence=confidence,
                speaker=speaker
            )

            transcript.words.append(newWord)

    def __wait_for_transcription_job(self, jobName):
        while True:
            job = self.__transcribeClient.get_transcription_job(
                TranscriptionJobName=jobName)

            status = job['TranscriptionJob']['TranscriptionJobStatus']

            if status in ['COMPLETED', 'FAILED']:
                break
            time.sleep(1)
        return status == 'COMPLETED', job

    def __s3_upload(self, inputPath, s3Path):
        exception = None
        fileUri = None
        try:
            self.__s3Client.upload_file(inputPath, self.bucketName, s3Path)

            pattern = "https://%s.s3.%s.amazonaws.com/%s"
            fileUri = pattern % self.bucketName, self.region_name, s3Path

        except Exception as e:
            message = "Media upload to Amazon failed : \n" + str(e)
            exception = exceptions.AmazonError(message)
        return fileUri, exception

    def set_vocabulary_file(self, vocabularyFilePath, lang="fr-FR"):
        exception = None
        if self.authenticated:
            with open(vocabularyFilePath) as vocabularyFile:
                self.__vocList = vocabularyFile.read().splitlines()

            filename = "ftvstt_voc_"
            filename = str(random.randint(1, 1e6))
            filename = "_"
            filename += os.path.basename(vocabularyFilePath).replace(".", "_")
            self.__vocName = filename
            exception = self.__create_vocabulary_file(lang)
        else:
            exception = exceptions.AmazonAuthError()

        if exception:
            self.__vocList = None
            raise exception

    def __create_vocabulary_file(self, lang):
        exception = None
        self.__transcribeClient.create_vocabulary(
            VocabularyName=self.__vocName,
            LanguageCode=lang,
            Phrases=self.__vocList
        )

        while True:
            status = self.__transcribeClient.get_vocabulary(
                VocabularyName=self.__vocName)

            if status['VocabularyState'] in ['READY', 'FAILED']:
                break
            time.sleep(1)

        if status['VocabularyState'] == 'FAILED':
            message = "Couldn't upload vocabulary file : \n"
            message += status['FailureReason']
            exception = exceptions.AmazonError(message)
        return exception

    def _make_language_compatible(self, lang):
        if lang[2] == '-':
            lang = lang[:2].lower() + lang[2:].upper()
        return lang
