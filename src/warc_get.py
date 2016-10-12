import os


def get_warc(url, name):
    """(str, str) -> str
    Generate the warc file of page content of given url, saved with the given 
    filr name. Return the name of the file. 
    """
    # Call the build in program Wget to generate warc file. Require Wget with 
    # version 1.14+.
    os.system("wget %s --warc-file='%s'" % (url, name))
    return title