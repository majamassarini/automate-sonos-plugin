import unittest  # noqa
import doctest
import soco_plugin


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(soco_plugin.command.play))
    tests.addTests(doctest.DocTestSuite(soco_plugin.command.pause))
    tests.addTests(doctest.DocTestSuite(soco_plugin.command.stop))
    tests.addTests(doctest.DocTestSuite(soco_plugin.command.playlist))
    tests.addTests(doctest.DocTestSuite(soco_plugin.command.mode))
    tests.addTests(doctest.DocTestSuite(soco_plugin.command.volume.absolute))
    tests.addTests(doctest.DocTestSuite(soco_plugin.command.volume.relative))
    tests.addTests(doctest.DocTestSuite(soco_plugin.command.volume.ramp))
    tests.addTests(doctest.DocTestSuite(soco_plugin.trigger.volume))
    tests.addTests(doctest.DocTestSuite(soco_plugin.message))
    tests.addTests(doctest.DocTestSuite(soco_plugin.gateway))

    return tests
