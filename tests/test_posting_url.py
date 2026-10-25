"""Scenario tests for scripts/posting_url.py (spec stellenanzeige-url UE-2, scenarios UE-A and UE-F)."""

import json
import os
import subprocess
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

    def test_remaining_parameters_keep_their_exact_bytes(self):
        base = "https://jobs.beispiel.example/j"
        for query in ("q=%E9", "flag", "a+b=1", "x=a%2Fb&y="):
            self.assertEqual(posting_url.clean(f"{base}?{query}&utm_source=x"), f"{base}?{query}", query)

    def test_encoded_tracking_key_is_removed(self):
        self.assertEqual(posting_url.clean("https://jobs.beispiel.example/j?id=1&%75tm_source=x"),
                         "https://jobs.beispiel.example/j?id=1")


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

    def test_linkedin_short_links_and_alternate_domains_refused(self):
        for url in ("https://lnkd.in/xyz", "https://www.linkedin.cn/jobs/1"):
            self.assertEqual(posting_url.refusal(url), posting_url.REFUSED_LINKEDIN, url)

    def test_encoded_hosts_refused(self):
        self.assertEqual(posting_url.refusal("http://%31%32%37.0.0.1/a"), posting_url.REFUSED_INTERNAL)
        self.assertEqual(posting_url.refusal("http://%6c%6f%63%61%6c%68%6f%73%74/"), posting_url.REFUSED_INTERNAL)
        self.assertEqual(posting_url.refusal("http://%256c%6f%63%61%6c%68%6f%73%74/"), posting_url.REFUSED_INTERNAL)
        self.assertEqual(posting_url.refusal("https://www.%6c%69%6e%6b%65%64%69%6e.com/jobs/1"),
                         posting_url.REFUSED_LINKEDIN)

    def test_file_downloads_refused(self):
        for url in ("https://karriere.musterfirma.example/stelle.pdf", "https://x.example/a/Stelle.PDF?v=2",
                    "https://x.example/a%2Eb/job.docx"):
            self.assertEqual(posting_url.refusal(url), posting_url.REFUSED_FILE, url)
        self.assertEqual(posting_url.refusal("https://x.example/jobs/pdf-entwickler"), "")

    def test_numeric_forms_do_not_depend_on_the_platform(self):
        self.assertEqual(str(posting_url.numeric_address("127.1")), "127.0.0.1")
        self.assertEqual(str(posting_url.numeric_address("0x7f.0.0.1")), "127.0.0.1")
        self.assertEqual(str(posting_url.numeric_address("0177.0.0.1")), "127.0.0.1")
        self.assertEqual(str(posting_url.numeric_address("2130706433")), "127.0.0.1")
        for host in ("1.2.3.4.5", "256.1.1.1", "1.2.3.999", "abc.def", "1.2.3.4junk", "08.1.1.1"):
            self.assertIsNone(posting_url.numeric_address(host), host)

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


class CommandLineTests(unittest.TestCase):
    def run_script(self, url):
        script = os.path.join(ROOT, "scripts", "posting_url.py")
        done = subprocess.run([sys.executable, "-I", script, url], capture_output=True, text=True, check=False)
        return done.returncode, json.loads(done.stdout)

    def test_allowed_url_exits_zero_with_the_cleaned_url(self):
        code, result = self.run_script("https://karriere.musterfirma.example/jobs/12345?utm_source=a")
        self.assertEqual(code, 0)
        self.assertEqual(result["bereinigt"], "https://karriere.musterfirma.example/jobs/12345")
        self.assertEqual(result["grund"], "")

    def test_refused_url_exits_three_with_a_reason(self):
        code, result = self.run_script("https://www.linkedin.com/jobs/view/123")
        self.assertEqual(code, 3)
        self.assertEqual(result["bereinigt"], "")
        self.assertEqual(result["grund"], posting_url.REFUSED_LINKEDIN)


if __name__ == "__main__":
    unittest.main()
