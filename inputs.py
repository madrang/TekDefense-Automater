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

#from outputs import SiteDetailOutput
from utilities import Utils, VersionChecker

__SITESXML__ = "sites.xml"
__REMOTE_SITESXML_LOCATION__ = "https://raw.githubusercontent.com/madrang/MadDefense-Automater/master/sites.xml"

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
            Utils.PrintStandardOutput("There was an error reading from the target input file."
                                        , verbose = verbose)

class SitesFile(object):
    """ SitesFile represents an XML Elementree object representing the program's configuration file.
    The sites.xml file is hosted on sites.com's github and unless asked otherwise,
            will be checked to ensure the versions are correct.
    If they are not, the new sites.xml will be downloaded and used by default.
    The local sites.xml is the user's capability to have local decisions made on top of the sites.xml configuration file.
    Switches will be created to enable and disable these capabilities.

    Method(s):
        (Class Method) getXMLTree
        (Class Method) fileExists

    Instance variable(s):
        No instance variables.
    """

    @classmethod
    def updateSitesDefenseXMLTree(cls, proxy = None, verbose = False):
        localmd5 = None
        try:
            localmd5 = VersionChecker.getMD5OfLocalFile(__SITESXML__)
        except IOError:
            Utils.PrintStandardOutput(f"Local file {__SITESXML__} not located."\
                        " Attempting download.", verbose = verbose)
        remotemd5 = None
        try:
            remotemd5 = SitesFile.getRemoteFile(__REMOTE_SITESXML_LOCATION__, proxy = proxy)
        except ConnectionError as ce:
            try:
                Utils.PrintStandardOutput(
                    f"Cannot connect to {__REMOTE_SITESXML_LOCATION__}."\
                        f" Server response is {ce.message[0]} Server error"\
                        f" code is {ce.message[1][0]}", verbose = verbose)
            except:
                Utils.PrintStandardOutput(
                    f"Cannot connect to {__REMOTE_SITESXML_LOCATION__} to retreive"\
                        f" the {__SITESXML__} for use.", verbose = verbose)
        except HTTPError as he:
            try:
                Utils.PrintStandardOutput(
                    f"Cannot connect to {__REMOTE_SITESXML_LOCATION__}."\
                        " Server response is {he.message}.", verbose = verbose)
            except:
                Utils.PrintStandardOutput(
                    f"Cannot connect to {__REMOTE_SITESXML_LOCATION__} to retreive"\
                        f" the {__SITESXML__} for use.", verbose = verbose)
        if localmd5:
            if not remotemd5:
                remotemd5 = VersionChecker.getMD5OfRemoteFile(__REMOTE_SITESXML_LOCATION__, proxy = proxy)
            if remotemd5 != localmd5:
                Utils.PrintStandardOutput(
                    f"There is an updated remote {__SITESXML__} file at {__REMOTE_SITESXML_LOCATION__}."\
                                " Attempting download.", verbose = verbose)
        else:
            Utils.PrintStandardOutput(
                f"Downloaded remote {__SITESXML__} file from {__REMOTE_SITESXML_LOCATION__}.", verbose = verbose)

    @classmethod
    def getRemoteFile(cls, location, proxy = None):
        if isinstance(proxy, str):
            proxy = {"https": proxy, "http": proxy}
        resp = requests.get(location, proxies = proxy, verify = False, timeout = 5)
        resp.raise_for_status()
        chunk_size = 65535
        md5Hash = hashlib.md5()
        with open(__SITESXML__, "wb") as fd:
            for chunk in resp.iter_content(chunk_size):
                fd.write(chunk)
                md5Hash.update(chunk)
        return md5Hash.hexdigest()


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
            Utils.PrintStandardOutput(f"No local {filename} file present.", verbose = verbose)
            return None
        try:
            with open(filename) as f:
                sitetree = ElementTree()
                sitetree.parse(f)
                return sitetree
        except:
            Utils.PrintStandardOutput(
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
