import os.path
import unittest
from unittest import mock

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from wagtail.documents import models


@override_settings(WAGTAILDOCS_SERVE_METHOD=None)
class TestServeView(TestCase):
    def setUp(self):
        self.document = models.Document(title="Test document", file_hash="123456")
        self.document.file.save('example.doc', ContentFile("A boring example document"))

    def tearDown(self):
        # delete the FieldFile directly because the TestCase does not commit
        # transactions to trigger transaction.on_commit() in the signal handler
        self.document.file.delete()

    def get(self):
        return self.client.get(reverse('wagtaildocs_serve', args=(self.document.id, self.document.filename)))

    def test_response_code(self):
        self.assertEqual(self.get().status_code, 200)

    def test_content_disposition_header(self):
        self.assertEqual(
            self.get()['Content-Disposition'],
            'attachment; filename="{}"'.format(self.document.filename))

    def test_content_length_header(self):
        self.assertEqual(self.get()['Content-Length'], '25')

    def test_content_type_header(self):
        self.assertEqual(self.get()['Content-Type'], 'application/msword')

    def test_is_streaming_response(self):
        self.assertTrue(self.get().streaming)

    def test_content(self):
        self.assertEqual(b"".join(self.get().streaming_content), b"A boring example document")

    def test_document_served_fired(self):
        mock_handler = mock.MagicMock()
        models.document_served.connect(mock_handler)

        self.get()

        self.assertEqual(mock_handler.call_count, 1)
        self.assertEqual(mock_handler.mock_calls[0][2]['sender'], models.Document)
        self.assertEqual(mock_handler.mock_calls[0][2]['instance'], self.document)

    def test_with_nonexistent_document(self):
        response = self.client.get(reverse('wagtaildocs_serve', args=(1000, 'blahblahblah', )))
        self.assertEqual(response.status_code, 404)

    def test_with_incorrect_filename(self):
        response = self.client.get(reverse('wagtaildocs_serve', args=(self.document.id, 'incorrectfilename')))
        self.assertEqual(response.status_code, 404)

    def test_has_etag_header(self):
        self.assertEqual(self.get()['ETag'], '"123456"')

    def test_has_cache_control_header(self):
        self.assertIn(self.get()['Cache-Control'], ['max-age=3600, public', 'public, max-age=3600'])

    def clear_sendfile_cache(self):
        from wagtail.utils.sendfile import _get_sendfile
        _get_sendfile.clear()


@override_settings(WAGTAILDOCS_SERVE_METHOD='redirect')
class TestServeViewWithRedirect(TestCase):
    def setUp(self):
        self.document = models.Document(title="Test document")
        self.document.file.save('example.doc', ContentFile("A boring example document"))
        self.serve_view_url = reverse('wagtaildocs_serve', args=(self.document.id, self.document.filename))

    def tearDown(self):
        self.document.delete()

    def get(self):
        return self.client.get(reverse('wagtaildocs_serve', args=(self.document.id, self.document.filename)))

    def test_document_url_should_point_to_serve_view(self):
        self.assertEqual(self.document.url, self.serve_view_url)

    def test_redirect(self):
        response = self.get()
        self.assertRedirects(response, self.document.file.url, fetch_redirect_response=False)


@override_settings(WAGTAILDOCS_SERVE_METHOD='direct')
class TestDirectDocumentUrls(TestCase):
    def setUp(self):
        self.document = models.Document(title="Test document")
        self.document.file.save('example.doc', ContentFile("A boring example document"))

    def tearDown(self):
        self.document.delete()

    def get(self):
        return self.client.get(reverse('wagtaildocs_serve', args=(self.document.id, self.document.filename)))

    def test_url_should_point_directly_to_file_storage_url(self):
        self.assertEqual(self.document.url, self.document.file.url)

    def test_redirect(self):
        # The serve view will not normally be linked to in 'direct' mode, but we should ensure it
        # still works by redirecting
        response = self.get()
        self.assertRedirects(response, self.document.file.url, fetch_redirect_response=False)


@override_settings(
    WAGTAILDOCS_SERVE_METHOD=None,
    DEFAULT_FILE_STORAGE='wagtail.tests.dummy_external_storage.DummyExternalStorage'
)
class TestServeWithExternalStorage(TestCase):
    """
    Test the behaviour of the default serve method when used with a remote storage backend
    (i.e. one that throws NotImplementedError for the path() method).
    """
    def setUp(self):
        self.document = models.Document(title="Test document")
        self.document.file.save('example.doc', ContentFile("A boring example document"))
        self.serve_view_url = reverse('wagtaildocs_serve', args=(self.document.id, self.document.filename))

    def tearDown(self):
        self.document.delete()

    def test_document_url_should_point_to_serve_view(self):
        self.assertEqual(self.document.url, self.serve_view_url)

    def test_redirect(self):
        # serve view should redirect to the remote URL
        response = self.client.get(self.serve_view_url)
        self.assertRedirects(response, self.document.file.url, fetch_redirect_response=False)


@override_settings(WAGTAILDOCS_SERVE_METHOD=None)
class TestServeViewWithSendfile(TestCase):
    def setUp(self):
        # Import using a try-catch block to prevent crashes if the
        # django-sendfile module is not installed
        try:
            import sendfile  # noqa
        except ImportError:
            raise unittest.SkipTest("django-sendfile not installed")

        self.document = models.Document(title="Test document")
        self.document.file.save('example.doc', ContentFile("A boring example document"))

    def tearDown(self):
        # delete the FieldFile directly because the TestCase does not commit
        # transactions to trigger transaction.on_commit() in the signal handler
        self.document.file.delete()

    def get(self):
        return self.client.get(reverse('wagtaildocs_serve', args=(self.document.id, self.document.filename)))

    def clear_sendfile_cache(self):
        from wagtail.utils.sendfile import _get_sendfile
        _get_sendfile.clear()

    @override_settings(SENDFILE_BACKEND='sendfile.backends.xsendfile')
    def test_sendfile_xsendfile_backend(self):
        self.clear_sendfile_cache()
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Sendfile'], self.document.file.path)

    @override_settings(
        SENDFILE_BACKEND='sendfile.backends.mod_wsgi',
        SENDFILE_ROOT=settings.MEDIA_ROOT,
        SENDFILE_URL=settings.MEDIA_URL[:-1]
    )
    def test_sendfile_mod_wsgi_backend(self):
        self.clear_sendfile_cache()
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Location'], os.path.join(settings.MEDIA_URL, self.document.file.name))

    @override_settings(
        SENDFILE_BACKEND='sendfile.backends.nginx',
        SENDFILE_ROOT=settings.MEDIA_ROOT,
        SENDFILE_URL=settings.MEDIA_URL[:-1]
    )
    def test_sendfile_nginx_backend(self):
        self.clear_sendfile_cache()
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Accel-Redirect'], os.path.join(settings.MEDIA_URL, self.document.file.name))


@override_settings(WAGTAILDOCS_SERVE_METHOD=None)
class TestServeWithUnicodeFilename(TestCase):
    def setUp(self):
        self.document = models.Document(title="Test document")

        self.filename = 'docs\u0627\u0644\u0643\u0627\u062a\u062f\u0631\u0627'
        '\u064a\u064a\u0629_\u0648\u0627\u0644\u0633\u0648\u0642'
        try:
            self.document.file.save(self.filename, ContentFile("A boring example document"))
        except UnicodeEncodeError:
            raise unittest.SkipTest("Filesystem doesn't support unicode filenames")

    def test_response_code(self):
        response = self.client.get(reverse('wagtaildocs_serve', args=(self.document.id, self.filename)))
        self.assertEqual(response.status_code, 200)
