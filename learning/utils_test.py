import unittest
import utils

class UtilsTest(unittest.TestCase):
    def test_striphtml(self):
        text = "<p>Det var god uppslutning p&aring; flygf&auml;ltet, &auml;ven om Henrik Brink, ordf&ouml;rande i Hudiksvalls MK, g&auml;rna hade sett lika m&aring;nga bilar till.</p> <p>&ndash; Det kostar</p>"
        result = utils.striphtml(text)
        expected = "Det var god uppslutning på flygfältet, även om Henrik Brink, ordförande i Hudiksvalls MK, gärna hade sett lika många bilar till. – Det kostar"
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
