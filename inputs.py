"""
The inputs.py module represents some form of all inputs
to the Automater program to include target files, and
the standard config file - sites.xml. Any addition to
Automater that brings any other input requirement should
be programmed in this module.

Class(es):
TargetFile -- Provides a representation of a file containing target
              strings for Automater to utilize.
SitesFile -- Provides a representation of the sites.xml
             configuration file.

Function(s):
No global exportable functions are defined.

Exception(s):
No exceptions exported.
"""
import os
import hashlib
import requests
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from xml.etree.ElementTree import ElementTree

from outputs import SiteDetailOutput
from utilities import VersionChecker

__REMOTE_TEKD_XML_LOCATION__ = "https://raw.githubusercontent.com/madrang/TekDefense-Automater/master/tekdefense.xml"
__TEKDEFENSEXML__ = "tekdefense.xml"

class TargetFile(object):
    """ TargetFile provides a Class Method to retrieve information from a file-based target when one is entered
            as the first parameter to the program.
    
    Public Method(s):
        (Class Method) TargetList
    
    Instance variable(s):
        No instance variables.
    """

    @classmethod
    def TargetList(self, filename, verbose = False):
        """ Opens a file for reading.
                Returns each string from each line of a single or multi-line file.

        Argument(s):
            filename -- string based name of the file that will be retrieved and parsed.
            verbose -- boolean value representing whether output will be printed to stdout

        Return value(s):
            Iterator of string(s) found in a single or multi-line file.
        """
        try:
            with open(filename) as file:
                lines = file.readlines()
                for li in lines:
                    yield str(li).strip()
        except IOError:
            SiteDetailOutput.PrintStandardOutput("There was an error reading from the target input file."
                                        , verbose = verbose)

class SitesFile(object):
    """ SitesFile represents an XML Elementree object representing the program's configuration file.
    The tekdefense.xml file is hosted on tekdefense.com's github and unless asked otherwise,
            will be checked to ensure the versions are correct.
    If they are not, the new tekdefense.xml will be downloaded and used by default.
    The local sites.xml is the user's capability to have local decisions made on top of the tekdefense.xml configuration file.
    Switches will be created to enable and disable these capabilities.

    Method(s):
        (Class Method) getXMLTree
        (Class Method) fileExists

    Instance variable(s):
        No instance variables.
    """

    @classmethod
    def updateTekDefenseXMLTree(cls, proxy = None, verbose = False):
        remotemd5 = None
        localmd5 = None
        localfileexists = False
        try:
            localmd5 = VersionChecker.getMD5OfLocalFile(__TEKDEFENSEXML__)
            localfileexists = True
        except IOError:
            SiteDetailOutput.PrintStandardOutput(f"Local file {__TEKDEFENSEXML__} not located. "\
                        "Attempting download.", verbose = verbose)
        try:
            if localfileexists:
                remotemd5 = VersionChecker.getMD5OfRemoteFile(__REMOTE_TEKD_XML_LOCATION__, proxy=proxy)
                if remotemd5 and remotemd5 != localmd5:
                    SiteDetailOutput.PrintStandardOutput(
                        f"There is an updated remote {__TEKDEFENSEXML__} file at {__REMOTE_TEKD_XML_LOCATION__}. "\
                                    "Attempting download.", verbose = verbose)
                    SitesFile.getRemoteFile(__REMOTE_TEKD_XML_LOCATION__, proxy)
            else:
                SitesFile.getRemoteFile(__REMOTE_TEKD_XML_LOCATION__, proxy)
        except ConnectionError as ce:
            try:
                SiteDetailOutput.PrintStandardOutput(
                    f"Cannot connect to {__REMOTE_TEKD_XML_LOCATION__}. "\
                        f"Server response is {ce.message[0]} Server error "\
                        f"code is {ce.message[1][0]}", verbose = verbose)
            except:
                SiteDetailOutput.PrintStandardOutput(
                    f"Cannot connect to {__REMOTE_TEKD_XML_LOCATION__} to retreive "\
                        f"the {__TEKDEFENSEXML__} for use.", verbose = verbose)
        except HTTPError as he:
            try:
                SiteDetailOutput.PrintStandardOutput(
                    f"Cannot connect to {__REMOTE_TEKD_XML_LOCATION__}. "\
                        "Server response is {he.message}.", verbose = verbose)
            except:
                SiteDetailOutput.PrintStandardOutput(
                    f"Cannot connect to {__REMOTE_TEKD_XML_LOCATION__} to retreive "\
                        f"the {__TEKDEFENSEXML__} for use.", verbose = verbose)

    @classmethod
    def getRemoteFile(cls, location, proxy = None):
        if isinstance(proxy, str):
            proxy = {"https": proxy, "http": proxy}
        resp = requests.get(location, proxies = proxy, verify = False, timeout = 5)
        resp.raise_for_status()
        chunk_size = 65535
        with open(__TEKDEFENSEXML__, "wb") as fd:
            for chunk in resp.iter_content(chunk_size):
                fd.write(chunk)

    @classmethod
    def getXMLTree(cls, filename, verbose = False):
        """ Opens a config file for reading.
            Returns XML Elementree object representing XML Config file.

        Argument(s):
            No arguments are required.
        
        Return value(s):
            ElementTree
        """
        if not SitesFile.fileExists(filename):
            SiteDetailOutput.PrintStandardOutput(f"No local {filename} file present.", verbose = verbose)
            return None
        try:
            with open(filename) as f:
                sitetree = ElementTree()
                sitetree.parse(f)
                return sitetree
        except:
            SiteDetailOutput.PrintStandardOutput(
                f"There was an error reading from the {filename} input file.\n"\
                f"Please check that the {filename} file is present and correctly formatted."
                                    , verbose = verbose)

    @classmethod
    def fileExists(cls, filename):
        """ Checks if a file exists.
            Returns boolean representing if file exists.
        
        Argument(s):
            No arguments are required.
        
        Return value(s):
            Boolean
        """
        return os.path.exists(filename) and os.path.isfile(filename)
