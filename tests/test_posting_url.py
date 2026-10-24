"""Scenario tests for scripts/posting_url.py (spec stellenanzeige-url UE-2, scenarios UE-A and UE-F)."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import posting_url  # noqa: E402


class CleanTests(unittest.TestCase):
    def test_ue_a_tracking_parameters_removed(self):
        url = "https://karriere.musterfirma.example/jobs/12345?utm_source=newsletter&utm_medium=mail"
        self.assertEqual(posting_url.clean(url), "https://karriere.musterfirma.example/jobs/12345")

    def test_identifying_parameters_stay(self):
        url = "https://jobs.beispiel.example/view?id=77&ref=abc&fbclid=x&gclid=y&mc_cid=z&trk=t"
        self.assertEqual(posting_url.clean(url), "https://jobs.beispiel.example/view?id=77&ref=abc")

    def test_unchanged_url_is_returned_as_given(self):
        url = "https://jobs.beispiel.example/view?id=77&ref=abc"
        self.assertEqual(posting_url.clean(url), url)

    def test_cleaning_that_leaves_no_path_or_id_keeps_the_url(self):
        url = "https://jobs.beispiel.example/?utm_source=a"
        self.assertEqual(posting_url.clean(url), url)

    def test_fragment_is_kept(self):
        url = "https://jobs.beispiel.example/job/5?utm_source=a#details"
        self.assertEqual(posting_url.clean(url), "https://jobs.beispiel.example/job/5#details")


class RefusalTests(unittest.TestCase):
    def test_public_url_is_allowed(self):
        self.assertEqual(posting_url.refusal("https://karriere.musterfirma.example/jobs/1"), "")
        self.assertEqual(posting_url.refusal("http://93.184.216.34/jobs/1"), "")

    def test_ue_f_linkedin_refused(self):
        for url in (
            "https://www.linkedin.com/jobs/view/123",
            "https://linkedin.com/jobs/view/123",
            "https://de.linkedin.com./jobs/view/123",
        ):
            self.assertEqual(posting_url.refusal(url), posting_url.REFUSED_LINKEDIN, url)

    def test_lookalike_host_is_not_linkedin(self):
        self.assertEqual(posting_url.refusal("https://notlinkedin.com/jobs/1"), "")

    def test_other_schemes_refused(self):
        for url in ("file:///etc/passwd", "ftp://beispiel.example/job", "javascript:alert(1)", "https:///nohost"):
            self.assertEqual(posting_url.refusal(url), posting_url.REFUSED_SCHEME, url)

    def test_internal_addresses_refused(self):
        for url in (
            "http://localhost:8080/job",
            "http://intranet.local/job",
            "http://127.0.0.1/job",
            "http://127.1/job",
            "http://2130706433/job",
            "http://0x7f000001/job",
            "http://10.0.0.5/job",
            "http://192.168.1.10/job",
            "http://172.16.3.4/job",
            "http://169.254.169.254/latest",
            "http://[::1]/job",
            "http://[fe80::1]/job",
        ):
            self.assertEqual(posting_url.refusal(url), posting_url.REFUSED_INTERNAL, url)


if __name__ == "__main__":
    unittest.main()
