# Text2Abstract - Mittmedia project

*An automated text processing tool, that exports a text/article to an abstract (with keywords). Article comming soon...*

## Method
The categorisation of the texts are are being tested with two methods, Part of speech clustring and K-means clustering. 
## Performance
### POS clustering
True positives:  3147
False positives:  2205

### FastText classification
The following table shows a confusion matrix of the evaluation:
| Ekonomi  | Sport | .       |
|:--------:|:-----:|:-------:|
| 7157     | 3243  | Ekonomi |
| 353      | 27518 | Sport   |

The accuracy, presicion and recall is calculated as:
```
tp = 7157
tn = 27518
fp = 3243
fn = 353
Accuracy = (tp + tn) / (tp + fp + tn + fn) 
         = 0.9060385148023308 ~ 91 %
Precision = tp / (tp + fp)
          = 0.6881730769230769
Recall = tp / (tp + fn)
       = 0.9529960053262317
F-score = 2 * Precision * Recall / (Precision + Recall)
        = 0.799218313791178
```
The way to achieve this accuracy in the method, FastText classification is to:
* First split your dataset into test and training sets (70/30). I used equal amount of articles in the categories _Sport_ and _Ekonomi_ (3000 for training and 10000 for testing)
* Convert the format so that it matches FastText or write an own method in fasttext source code
* Compile fasttext
    * make clean opt
* Train fasttext with 30 % of the dataset
* Test fasttext with 70 % of the dataset

### K-means clustering
The following table shows a confusion matrix of the evaluation:
| Ekonomi | Sport  | .       |
|:-------:|:------:|:-------:|
| 9639    | 122    | Ekonomi |
| 3594    | 27939  | Sport   |

The accuracy, presicion and recall is calculated as:
```
tp = 9639
tn = 27939
fp = 122
fn = 3594
Accuracy = (tp + tn) / (tp + fp + tn + fn) 
         = 0.9126353619898804 ~ 91 %
Precision = tp / (tp + fp)
          = 0.9875012806064952
Recall = tp / (tp + fn)
       = 0.7284062570845613
F-score = 2 * Precision * Recall / (Precision + Recall)
        = 0.838392624162825
```
The way to achieve this accuracy in the method, k-means clustering is to:
* First train a doc2vec model linrearly with a 10k article database with the categories _Sport_ and _Ekonomi_ as is described in [here](https://rare-technologies.com/doc2vec-tutorial/)
   * Parameter **alpha** = 0.025
   * Parameter **min_alpha** = 0.025
* Train the k-means model with the 2k first articles in the database. The articles are transformed into a summarized article using PyTeaser and then converted into wordvectors that can be achieved from the doc2vec model. The distance we use in k-means algoritm is the inverse cosine similarity as distance (*)
   * Parameter **iterations** = 15
   * Parameter **number_of_clusters** = 2
* Evaluate the results by predict the category of the rest 8k articles left in the database by categorise these by the centroid recieved from the k-means model

> (*) cosine similarity has the similarity interval between [-1,1] and k-means wants to minimize the distance to zero while 1 means most similarity. The way we define the inverse is by calculating the similarity _inv\_similarity_ as: 
`inv_similarity = 1 - (similarity + 1) / 2`

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