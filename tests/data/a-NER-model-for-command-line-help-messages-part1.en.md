---
title: "A NER Model for Command Line Help Messages (Part 1: The command line program)"
date: 2023-02-21T18:55:27+01:00
draft: false
categories: ["NLP"]
tags: ["NLP", "NER", "spaCy", "Python", "rich"]
---

In this 3 part series I will tell the journey of creating a program to detect the different 
components/entities of a command line program's help message. This post will start by looking at the final 
product [helpner](https://github.com/plaguss/helpner), a python program that can be installed 
from [PyPI](https://pypi.org/project/helpner/), the second will tell about the spaCy NLP workflow 
and finally we will take a look at the data that feeds spaCy's final model.

> *The post assumes some python knowledge, like how to install a library from PyPI,*
> *and some familiarity with spaCy.*

The following figure shows the architecture of helpner, each piece is represented by a different
github repository. Highlighted in yellow at the bottom its the piece corresponding to
[helpner](https://github.com/plaguss/helpner).

![helpner](/images/helpner-arch-part1.png)

### What led me to start this project?

I wanted an NLP project to put into practice the spaCy facilities. If possible, the
model should be ready to use by an end user without developing a website for it
for simplicity. Independently, I found [docopt](http://docopt.org/) by chance exploring
python CLI libraries. As it turns out, this library, and its maintained fork ([docopt-ng](https://github.com/jazzband/docopt-ng))
can generate a CLI program by parsing a "properly written" help message (visit the previous
link to see an example). This same idea seemed like a good opportunity.

> Can we solve this using a [Named Entity Recognition](https://spacy.io/usage/linguistic-features#named-entities) model? *...I don't care if its not the best approach*

Lets try to write a CLI program that can take a help message from another
CLI program, and find the different elements or entities (`commands`, `arguments` and `options`)
which conform it. It turns out that in around 200 lines of code, we can have a promising
first version :smile:. Of course, this is not that simple, but with spaCy it feels like it :ok_hand:.

### Enter helpner

Lets see how [helpner](https://github.com/plaguss/helpner) works. 
The installation consists of two steps. First, install using *pip* as usual
preferably inside a venv. (It should be possible to install it using
[pipx](https://pypa.github.io/pipx/), but I haven't tried it yet):

```console
$ pip install helpner
```

This should have downloaded the library, but as of this moment its incomplete,
we still have to download the model itself. For this, a handy command is supplied
(visit the README.md for more information):

```console
$ helpner download
```

This two step process should be familiar for those who have already used [spaCy](https://spacy.io/). By using
this approach it allows to split the development of the model from the use we make of
it. We could update the model in any way (we could for example retrain the model with different
data, or modify the optimizer used), and we would only need to update the model (running again the download command). It applies
the same for the library, we could add more functionality without changing the inner model.

We are already in position to use *helpner* :collision:, lets see one of the examples
from the docs, how to highlight the entities of a help message (this was the first use that came to mind):

```sh
flit install --help | helpner highlight
```

![flit-install-help](/images/flit-install-help.svg)

For those who don't know [flit](https://github.com/pypa/flit), its a command line program that 
simplifies packaging python modules. The example shows the help message of one of its subcommands, 
`flit install`. From the legend we see that the possible elements or entities are CMD (commands 
or subcommands, which in this case depend on `flit` directly), `ARG` (positional arguments, 
which in this case don't exist) and `OPT` (optional arguments, which correspond to all the elements 
preceded by a single or double dash, are correctly predicted). But it calls the attention some 
random words highlighted as if they were `CMD` entities, which are clearly misplaced. It is far from
perfect, but I consider it a success anyway, the results seem promising enough!

What happens underneath? what we did was send the help message to the *spaCy* model,
and get the predictions:

```console
❯ flit install --help | helpner parse --no-json
{
    'install': ('CMD', 12, 19),
    '[-h]': ('OPT', 20, 24),
    '[-s]': ('OPT', 25, 29),
    '[--pth-file]': ('OPT', 30, 42),
    '[--user]': ('OPT', 43, 51),
    '[--env]': ('OPT', 52, 59),
    '[--python PYTHON]': ('OPT', 60, 77),
    '[--deps {all,production,develop,none}]': ('OPT', 98, 136),
    '[--only-deps]': ('OPT', 137, 150),
    '[--extras EXTRAS]': ('OPT', 171, 188),
    '-h, --help': ('OPT', 201, 211),
    'exit': ('CMD', 250, 254),
    '-s, --symlink': ('OPT', 257, 270),
    'package': ('CMD', 298, 305),
    '--pth-file': ('OPT', 373, 383),
    'module': ('CMD', 417, 423),
    '/': ('CMD', 423, 424),
    '--user': ('OPT', 497, 503),
    'local': ('CMD', 529, 534),
    '--env': ('OPT', 612, 617),
    '--python PYTHON': ('OPT', 749, 764),
    '--deps {all,production,develop,none}': ('OPT', 862, 898),
    '--only-deps': ('OPT', 1074, 1085),
    '--extras EXTRAS': ('OPT', 1192, 1207),
    'the': ('CMD', 1313, 1316),
    'ones': ('CMD', 1317, 1321),
    'implied': ('CMD', 1322, 1329),
    'by': ('CMD', 1330, 1332),
    'be': ('CMD', 1382, 1384),
    'useful': ('CMD', 1385, 1391)
}
```

This output has all the necessary information to inform `rich`. The keys in the dict
correspond to the elements found/predicted, and the values contain the entity, start
and end position of the substrings. With this information, we can make use of 
[rich](https://rich.readthedocs.io/en/stable/introduction.html) to add some color to the console.

Of course, there are multiple errors (and this is an example that seems relatively
right), the model cannot be better than the data it was fed with. In a posterior post
we will see how the data powering this model is obtained.

<!-- ### Related posts

add here -->

