# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for the command-line scripts in the top-level I{bin/} directory.

Tests for actual functionality belong elsewhere, written in a way that doesn't
involve launching child processes.
"""

from os import devnull, getcwd, chdir
from sys import executable
from subprocess import PIPE, Popen

from twisted.trial.unittest import SkipTest, TestCase
from twisted.python.modules import getModule
from twisted.python.filepath import FilePath


class ScriptTestsMixin:
    """
    Mixin for L{TestCase} subclasses which defines a helper function for testing
    a Twisted-using script.
    """
    bin = getModule("twisted").pathEntry.filePath.child("bin")

    def scriptTest(self, name):
        """
        Verify that the given script runs and uses the version of Twisted
        currently being tested.

        This only works when running tests against a vcs checkout of Twisted,
        since it relies on the scripts being in the place they are kept in
        version control, and exercises their logic for finding the right version
        of Twisted to use in that situation.

        @param name: A path fragment, relative to the I{bin} directory of a
            Twisted source checkout, identifying a script to test.
        @type name: C{str}

        @raise SkipTest: if the script is not where it is expected to be.
        """
        script = self.bin.preauthChild(name)
        if not script.exists():
            raise SkipTest(
                "Script tests do not apply to installed configuration.")

        from twisted.copyright import version
        scriptVersion = Popen(
            [executable, script.path, '--version'],
            stdout=PIPE, stderr=file(devnull)).stdout.read()

        self.assertIn(str(version), scriptVersion)



class ScriptTests(TestCase, ScriptTestsMixin):
    """
    Tests for the core scripts.
    """
    def test_mktap(self):
        self.scriptTest("mktap")


    def test_twistd(self):
        self.scriptTest("twistd")


    def test_twistdPathInsert(self):
        """
        The twistd script adds the current working directory to sys.path so
        that it's able to import modules from it.
        """
        script = self.bin.child("twistd")
        if not script.exists():
            raise SkipTest(
                "Script tests do not apply to installed configuration.")
        cwd = getcwd()
        self.addCleanup(chdir, cwd)
        testDir = FilePath(self.mktemp())
        testDir.makedirs()
        chdir(testDir.path)
        testDir.child("bar.tac").setContent(
            "import sys\n"
            "print sys.path\n")
        output = Popen(
            [executable, script.path, '-ny', 'bar.tac'],
            stdout=PIPE, stderr=file(devnull)).stdout.read()
        self.assertIn(repr(testDir.path), output)


    def test_manhole(self):
        self.scriptTest("manhole")


    def test_trial(self):
        self.scriptTest("trial")


    def test_trialPathInsert(self):
        """
        The trial script adds the current working directory to sys.path so that
        it's able to import modules from it.
        """
        script = self.bin.child("trial")
        if not script.exists():
            raise SkipTest(
                "Script tests do not apply to installed configuration.")
        cwd = getcwd()
        self.addCleanup(chdir, cwd)
        testDir = FilePath(self.mktemp())
        testDir.makedirs()
        chdir(testDir.path)
        testDir.child("foo.py").setContent("")
        output = Popen(
            [executable, script.path, 'foo'],
            stdout=PIPE, stderr=file(devnull)).stdout.read()
        self.assertIn("PASSED", output)


    def test_pyhtmlizer(self):
        self.scriptTest("pyhtmlizer")


    def test_tap2rpm(self):
        self.scriptTest("tap2rpm")


    def test_tap2deb(self):
        self.scriptTest("tap2deb")


    def test_tapconvert(self):
        self.scriptTest("tapconvert")
