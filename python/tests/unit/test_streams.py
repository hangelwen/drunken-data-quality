import sys
import unittest
from mock import Mock

from pyddq.streams import FileOutputStream, ByteArrayOutputStream, OutputStream


class OutputStreamTest(unittest.TestCase):
    def test_jvm_obj(self):
        # check that AttributeError is raised
        # when jvm is set more than once for the same instance
        stream = OutputStream()
        with self.assertRaises(AttributeError):
            stream.jvm = 1
            stream.jvm = 2


class FileOutputStreamTest(unittest.TestCase):
    def test_constructor(self):
        self.assertRaisesRegexp(ValueError, "Descriptor is not a file",
                                FileOutputStream, "not a file")

        descriptor = Mock(spec=file, closed=True)
        self.assertRaisesRegexp(ValueError, "Descriptor is closed",
                                FileOutputStream, descriptor)

        descriptor = Mock(spec=file, closed=False, mode="r")
        self.assertRaisesRegexp(ValueError, "Descriptor is opened for reading",
                                FileOutputStream, descriptor)

        descriptor = Mock(spec=file, closed=False, mode="w")
        stream = FileOutputStream(descriptor)
        self.assertEqual(stream.descriptor, descriptor)

    def test_jvm_obj(self):
        jvm = Mock()
        stdout = Mock(spec=file, mode="w", closed=False)
        stdout.name="<stdout>"
        fos = FileOutputStream(stdout)
        # check that AttributeError is raised
        # when jvm_obj is accessed before jvm is set
        with self.assertRaises(AttributeError):
            jvm_obj = fos.jvm_obj

        # check that stdout mapping works fine
        fos.jvm = jvm
        jvm_obj = fos.jvm_obj
        self.assertEqual(jvm_obj, jvm.System.out)

        # check that file descriptor is converted to FileOutputStream
        descriptor = Mock(spec=file, mode="w", closed=False)

        jvmFileOutputStream = Mock()
        jvm.java.io.FileOutputStream = jvmFileOutputStream
        fos = FileOutputStream(descriptor)
        fos.jvm = jvm
        jvm_obj = fos.jvm_obj
        self.assertEqual(jvm_obj, jvmFileOutputStream())

        # check that on the second call FileOutputStream returns the same jvm_obj
        jvm.java.io.FileOutputStream = Mock(
            sides_effects=[1, 2]
        )
        fos = FileOutputStream(descriptor)
        fos.jvm = jvm

        jvm_obj1 = fos.jvm_obj
        jvm_obj2 = fos.jvm_obj
        self.assertEqual(jvm_obj1, jvm_obj2)


class ByteArrayOutputStreamTest(unittest.TestCase):
    def test_jvm_obj(self):
        jvm = Mock()

        baos = ByteArrayOutputStream()
        with self.assertRaises(AttributeError):
            jvm_obj = baos.jvm_obj

        # check that on the second call ByteArrayOutputStream returns the same jvm_obj
        jvm.java.io.ByteArrayOutputStream = Mock(
            side_effects=[1, 2]
        )
        baos.jvm = jvm
        jvm_obj1 = baos.jvm_obj
        jvm_obj2 = baos.jvm_obj
        self.assertEqual(jvm_obj1, jvm_obj2)

    def test_get_output(self):
        jvm = Mock()
        baos = ByteArrayOutputStream()
        baos.jvm = jvm

        baos.get_output()
        baos.jvm_obj.toString().strip.assert_called()
