# Text2Abstract - Mittmedia project

*An automated text processing tool, that exports a text/article to an abstract (with keywords). Article comming soon...*

## Performance

## Installation

Running and training Text2Abstract model requires you to install the following packages:

*   python 2.7:
*   pip (python package manager)
    * `apt-get install python-pip` on Ubuntu
    * `brew` installs pip along with python on OSX
*   bazel **with a version supported by [syntaxnet](https://github.com/tensorflow/models/tree/master/syntaxnet)*
    *   You can follow the instructions [here](http://bazel.io/docs/install.html)
*   swig:
    *   `apt-get install swig` on Ubuntu
    *   `brew install swig` on OSX
*   protocol buffers **with a version supported by [TensorFlow](https://www.tensorflow.org/) dependency:*
    *   check your protobuf version with `pip freeze | grep protobuf`
    *   upgrade to a supported version with `pip install -U protobuf==3.0.0b2`
*   asciitree, to draw parse trees on the console for the demo:
    *   `pip install asciitree`
*   numpy, package for scientific computing:
    *   `pip install numpy`

**Note:** If you are running Docker on OSX, make sure that you have enough
memory allocated for your Docker VM.

## Getting Started

### Training the Text2Abstract model

## Contact
**Johannes Lindén** [johannes@godesity.se](mailto:johannes@godesity.se)
## Credits

A list of valuable contributors:

*   Johannes Lindén
*   Michelle Ludovici
*   Magnus Engström