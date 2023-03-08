# Overview

This section shows a guided example using the CLI and the python API.

First of all, make sure that the [spanglish](https://github.com/plaguss/spanglish) service is up and running (take a look to the guide if you haven't done it yet). Using docker compose, un a separate window run `docker compose up`.

## CLI

For convenience, a command line app can be installed, with the functionality just to translate a markdown file for the moment (check the README file for the installation instructions):


## Python API


### Instantiate the client

Lets start by importing the code 

```python
>>> from translate_md.client import SpanglishClient
>>> client = SpanglishClient()
>>> client
SpanglishClient(http://localhost:8000/) 
```

By default it assumes the server is running on *http://localhost:8000/*.

### Translate a piece of text

```python
>>> michael_scott = """Sometimes I'll start a sentence and I don't even know where it's going. I just hope I find it along the way."""
>>> client.translate(michael_scott)

TODO
```

### Translate a batch of texts

```python
>>> dwitght_schrute = """Whenever I'm about to do something, I think, 'Would an idiot do that?' and if they would, I do not do that thing."""
>>> michael_scott = """I knew exactly what to do, but in a much more real sense I had no idea what to do."""
>>> andy_bernard = "Sorry I annoyed you with my friendship"
>>> jim_halpert = "Bears, beets, Battlestar Galactica."
>>> creed_bratton = """Oh, you’re paying way too much for worms. Who’s your worm guy?"""
>>> oscar_martinez = """I consider myself a good person, but I'm gonna try to make him cry."""
>>> prison_mike = "The worst thing about prison was the Dementors."
>>> kelly_kapoor = """Who says exactly what they’re thinking? What kind of a game is that?"""
>>> stanley_hudson = """Boy, have you done lost your mind? Cause I’ll help you find it!"""
>>> client.translate_batch([
    dwitght_schrute, michael_scott, andy_bernard, jim_halpert,
    creed_bratton, oscar_martinez, prison_mike, kelly_kapoor,
    stanley_hudson
])

TODO
```

### Translate a markdown file

The following example uses a sample file placed in the tests folder of this repo. You can copy the content to a file and change the *filename* variable appropriately to run the example (If new_filename argument is not given if will be automatically generated, in this case changing the name to `post-example.es.md` on the same directory):

```python
>>> from pathlib import Path
>>> filename = Path.cwd() / "tests/data/post-example.md"
>>> new_filename = Path.home() / "Downloads" / "example_file.es.md"
>>> client.translate_file(filename, new_filename=new_filename)
```

TODO: Write result before and after

