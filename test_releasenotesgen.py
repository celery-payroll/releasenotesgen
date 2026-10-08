import io
import os
import tempfile
import unittest
from unittest import mock

import releasenotesgen


class LoadConfigTestCase(unittest.TestCase):
    """
    Runs load_config() against a temporary releasenotesgen.yml.
    API keys and the OpenAI client are faked so no network is involved.
    """

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.orig_cwd = os.getcwd()
        os.chdir(self.tmp_dir.name)
        patches = [
            mock.patch.dict(os.environ, {'GITHUB_TOKEN': 'gh', 'OPENAI_API_KEY': 'oa'}),
            mock.patch.object(releasenotesgen, 'OpenAI'),
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def tearDown(self):
        os.chdir(self.orig_cwd)
        self.tmp_dir.cleanup()

    def write_yml(self, content):
        with open('releasenotesgen.yml', 'w') as config_file:
            config_file.write(content)

    def test_system_prompt_defaults_to_builtin_when_key_absent(self):
        self.write_yml("repo_owner: acme\nrepo_name: widgets\n")

        releasenotesgen.load_config()

        self.assertEqual(releasenotesgen.SYSTEM_PROMPT, releasenotesgen.DEFAULT_SYSTEM_PROMPT)

    def test_system_prompt_is_taken_verbatim_from_yml(self):
        self.write_yml(
            "repo_owner: acme\nrepo_name: widgets\n"
            "system_prompt: |\n  Line one.\n\n  Line two.\n"
        )

        releasenotesgen.load_config()

        self.assertEqual(releasenotesgen.SYSTEM_PROMPT, "Line one.\n\nLine two.\n")

    def assert_rejects_system_prompt(self, yaml_value):
        self.write_yml(f"repo_owner: acme\nrepo_name: widgets\nsystem_prompt: {yaml_value}\n")

        with mock.patch('sys.stdout', new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as raised:
                releasenotesgen.load_config()

        self.assertEqual(raised.exception.code, 1)
        self.assertIn('system_prompt', stdout.getvalue())

    def test_empty_system_prompt_exits_with_error_naming_the_key(self):
        self.assert_rejects_system_prompt('""')

    def test_whitespace_only_system_prompt_exits_with_error_naming_the_key(self):
        self.assert_rejects_system_prompt('"   \n"')

    def test_non_string_system_prompt_exits_with_error_naming_the_key(self):
        self.assert_rejects_system_prompt('[a, b]')


class SummarizeIssueTestCase(unittest.TestCase):
    """
    Checks the OpenAI call made by summarize_issue() with a fake client.
    """

    def test_sends_configured_system_prompt_as_system_message(self):
        fake_client = mock.Mock()
        fake_client.chat.completions.create.return_value.choices = [
            mock.Mock(message=mock.Mock(content='  note  '))
        ]
        with mock.patch.multiple(
            releasenotesgen, client=fake_client, MODEL='m', SYSTEM_PROMPT='Custom prompt.'
        ):
            summary = releasenotesgen.summarize_issue('Title', 'Body')

        messages = fake_client.chat.completions.create.call_args.kwargs['messages']
        self.assertEqual(messages[0], {'role': 'system', 'content': 'Custom prompt.'})
        self.assertEqual(summary, 'note')


if __name__ == '__main__':
    unittest.main()
