""" The utilities.py module handles all utility functions that Automater requires.

Class(es):
    Parser -- Class to handle standard argparse functions with a class-based structure.
    IPWrapper -- Class to provide IP Address formatting and parsing.
    VersionChecker -- Class to check if modifications to any files are available

Function(s):
    No global exportable functions are defined.

Exception(s):
    No exceptions exported.
"""
import argparse
import re
import os
import hashlib
import requests

class Parser:
    """ Parser represents an argparse object representing the program's input parameters.

    Public Method(s):
        print_help
        (Property) hasBotOut
        (Property) HTMLOutFile
        (Property) TextOutFile
        (Property) CSVOutFile
        (Property) Delay
        (Property) Proxy
        (Property) Target
        (Property) hasInputFile
        (Property) Source
        (Property) InputFile
        (Property) UserAgent

    Instance variable(s):
        _parser
        args
    """

    def __init__(self, desc, version):
        """ Class constructor.
            Adds the argparse info into the instance variables.

        Argument(s):
            desc -- ArgumentParser description.
        """
        self._parser = argparse.ArgumentParser(description = desc)
        self._parser.add_argument("target"
            , help = "List one IP Address (CIDR or dash notation accepted), URL or Hash to query or pass the filename"\
                " of a file containing IP Address info, URL or Hash to query each separated by a newline.")
        self._parser.add_argument("-o", "--output"
            , help = "This option will output the results to a file.")
        self._parser.add_argument("-b", "--bot", action = "store_true"
            , help = "This option will output minimized results for a bot.")
        self._parser.add_argument("-f", "--cef"
            , help = "This option will output the results to a CEF formatted file.")
        self._parser.add_argument("-w", "--web"
            , help = "This option will output the results to an HTML file.")
        self._parser.add_argument("-c", "--csv"
            , help = "This option will output the results to a CSV file.")
        self._parser.add_argument("-d", "--delay", type = int, default = 2
            , help = "This will change the delay to the inputted seconds. Default is 2.")
        self._parser.add_argument("-s", "--source"
            , help = "This option will only run the target against a specific source engine to pull associated domains."\
                    " Options are defined in the name attribute of the site element in the XML configuration file."\
                        " This can be a list of names separated by a semicolon.")
        self._parser.add_argument("--proxy"
            , help = "This option will set a proxy to use (eg. proxy.example.com:8080)")
        self._parser.add_argument("-a", "--useragent", default = f"Automater/{version}"
            , help="This option allows the user to set the user-agent seen by web servers being utilized."\
                    " By default, the user-agent is set to Automater/version")
        self._parser.add_argument("-V", "--vercheck", action = "store_true"
            , help="This option checks and reports versioning for Automater."\
                    " Checks each python module in the Automater scope.")
        self._parser.add_argument("-r", "--refreshxml", action = "store_true"
            , help = "This option refreshes the sites.xml file from the remote GitHub site.")
        self._parser.add_argument("-v", "--verbose", action = "store_true"
            , help = "This option prints debug messages to the screen.")
        self.args = self._parser.parse_args()

    def print_help(self):
        """ Returns standard help information to determine usage for program.

        Argument(s):
            No arguments are required.

        Return value(s):
            string -- Standard argparse help information to show program usage.
        """
        self._parser.print_help()

    @property
    def hasBotOut(self):
        """ Checks to determine if user requested an output file minimized for use with a Bot.
            Returns True if user requested minimized Bot output, False if not.

        Return value(s):
            Boolean
        """
        return True if self.args.bot else False

    @property
    def CEFOutFile(self):
        """ Checks if there is an CEF output requested.
            Returns string name of CEF output file if requested or None if not requested.

        Return value(s):
            string -- Name of an output file to write to system.
            None -- if CEF output was not requested.
        """
        return self.args.cef if self.args.cef else None

    @property
    def CSVOutFile(self):
        """ Checks if there is a comma delimited output requested.
            Returns string name of comma delimited output file if requested or None if not requested.

        Return value(s):
            string -- Name of an comma delimited file to write to system.
            None -- if comma delimited output was not requested.
        """
        return self.args.csv if self.args.csv else None

    @property
    def HTMLOutFile(self):
        """ Checks if there is an HTML output requested.
            Returns string name of HTML output file if requested or None if not requested.

        Return value(s):
            string -- Name of an output file to write to system.
            None -- if web output was not requested.
        """
        return self.args.web if self.args.web else None

    @property
    def TextOutFile(self):
        """ Checks if there is a text output requested.
            Returns string name of text output file if requested or None if not requested.

        Return value(s):
            string -- Name of an output file to write to system.
            None -- if output file was not requested.
        """
        return self.args.output if self.args.output else None

    @property
    def VersionCheck(self):
        """ Checks to determine if the user wants the program to check for versioning.
            By default this is True which means the user wants to check for versions.

        Return value(s):
            Boolean
        """
        print(f"VersionCheck: {self.args.vercheck}")
        return True if self.args.vercheck else False

    @property
    def Verbose(self):
        """ Checks to determine if the user wants the program to send standard output to the screen.

        Return value(s):
            Boolean
        """
        return True if self.args.verbose else False

    @property
    def RefreshRemoteXML(self):
        """ Checks to determine if the user wants the program to grab the sites.xml information each run.

        Return value(s):
            Boolean
        """
        return True if self.args.refreshxml else False

    @property
    def Delay(self):
        """ Returns delay set by input parameters to the program.

        Return value(s):
            string -- String containing integer to tell program how long to delay between each site query.
                        Default delay is 2 seconds.
        """
        return self.args.delay

    @property
    def Proxy(self):
        """ Returns proxy set by input parameters to the program.

        Return value(s):
            string -- String containing proxy server in format server:port, default is none
        """
        return self.args.proxy if self.args.proxy else None

    @property
    def Target(self):
        """ Checks to determine the target info provided to the program.
            Returns string name of target or string name of file or None if a target is not provided.

        Return value(s):
            string -- String target info or filename based on target parameter to program.
        """
        return self.args.target if self.args.target else None

    @property
    def hasInputFile(self):
        """ Checks to determine if input file is the target of the program.
            Returns True if a target is an input file, False if not.

        Argument(s):
            No arguments are required.

        Return value(s):
            Boolean
        """
        return True if os.path.exists(self.args.target) and os.path.isfile(self.args.target) else False

    @property
    def Source(self):
        """ Checks to determine if a source parameter was provided to the program.
            Returns string name of source or None if a source is not provided

        Return value(s):
            string -- String source name based on source parameter to program.
            None -- If the -s parameter is not used.
        """
        return self.args.source if self.args.source else None

    @property
    def InputFile(self):
        """ Checks to determine if an input file string representation of a target was provided as a parameter to the program.
            Returns string name of file or None if file name is not provided

        Return value(s):
            string -- String file name based on target filename parameter to program.
            None -- If the target is not a filename.
        """
        return None if not self.Target or not self.hasInputFile() else self.Target

    @property
    def UserAgent(self):
        """ Returns useragent setting invoked by user at command line or the default user agent provided by the program.

        Return value(s):
            string -- Name utilized as the useragent for the program.
        """
        return self.args.useragent

class Utils:
    """
    """
    @classmethod
    def PrintStandardOutput(cls, strout, *args, **kwargs):
        """
        """
        if "verbose" in list(kwargs.keys()):
            if kwargs["verbose"] is True:
                print(strout)
            else:
                return
        else:
            print(strout)

class IPWrapper:
    """ IPWrapper provides Class Methods to enable checks against strings to determine if the string
            is an IP Address or an IP Address in CIDR or dash notation.

    Public Method(s):
        (Class Method) isIPorIPList
        (Class Method) getTarget

    Instance variable(s):
        No instance variables.
    """
    #_ipRangePrefix = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}")
    _ipRangeDash = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}")
    _ipAddress = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

    @classmethod
    def isIPorIPList(cls, target):
        """ Checks if an input string is an IP Address or if it is an IP Address in CIDR or dash notation.
            Returns True if IP Address or CIDR/dash. Returns False if not.

        Argument(s):
            target -- string target provided as the first argument to the program.

        Return value(s):
            Boolean
        """
        #ipRgeFind = re.findall(IPWrapper._ipRangePrefix, target)             # IP Address range using prefix syntax
        #if ipRgeFind is not None and len(ipRgeFind) > 0:
        #    return True

        ipRgeDashFind = re.findall(IPWrapper._ipRangeDash, target)
        if ipRgeDashFind is not None and len(ipRgeDashFind) > 0:
            return True

        ipFind = re.findall(IPWrapper._ipAddress, target)
        if ipFind is not None and len(ipFind) > 0:
            return True

        return False

    @classmethod
    def getTarget(cls, target):
        """ Determines whether the target provided is an IP Address or an IP Address in dash notation.
            Then creates a list that can be utilized as targets by the program.
            Returns a list of string IP Addresses that can be used as targets.

        Argument(s):
            target -- string target provided as the first argument to the program.

        Return value(s):
            Iterator of string(s) representing IP Addresses.
        """
        # IP Address range using prefix syntax
        ipRgeDashFind = re.findall(IPWrapper._ipRangeDash, target)
        # IP Address range seperated with a dash
        if ipRgeDashFind is not None and len(ipRgeDashFind) > 0:
            iplist = target[:target.index("-")].split(".")
            iplast = target[target.index("-") + 1:]
            if int(iplist[3]) < int(iplast):
                for lastoctet in range(int(iplist[3]), int(iplast) + 1):
                    yield target[:target.rindex(".") + 1] + str(lastoctet)
            else:
                yield target[:target.rindex(".") + 1] + str(iplist[3])
        else: # it's just an IP address at this point
            yield target

class VersionChecker:
    """ Uses MD5 to indicate if any files needs to be updated.
    Public Method(s):
        (Class Method) isIPorIPList
        (Class Method) getTarget

    Instance variable(s):
        No instance variables.
    """
    @classmethod
    def checkModules(self, prefix, gitlocation, proxy = None, verbose = False):
        execpath = os.path.dirname(os.path.realpath(__file__))
        pythonfiles = [f for f in os.listdir(execpath) if os.path.isfile(os.path.join(execpath, f)) and f[-3:] == ".py"]
        try:
            modifiedfiles = VersionChecker.getModifiedFileInfo(prefix, gitlocation, pythonfiles, proxy = proxy)
            if modifiedfiles is None or len(modifiedfiles) == 0:
                Utils.PrintStandardOutput(
                            "All Automater files are up to date"
                                        , verbose = verbose)
            else:
                Utils.PrintStandardOutput(
                    f"The following files require update: {", ".join(modifiedfiles)}."\
                        f"\nSee {gitlocation} to update these files"
                                    , verbose = verbose)
        except:
            Utils.PrintStandardOutput(
                f"There was an error while checking the version of the Automater files."\
                    f" Please see {gitlocation} to check if the files are still online."
                                    , verbose = verbose)
            raise

    @classmethod
    def getModifiedFileInfo(cls, prefix, gitlocation, filelist, proxy = None):
        modifiedfiles = []
        for filename in filelist:
            md5local = VersionChecker.getMD5OfLocalFile(filename)
            md5remote = VersionChecker.getMD5OfRemoteFile(prefix + filename, proxy)
            if md5local != md5remote:
                modifiedfiles.append(filename)
        return modifiedfiles if len(modifiedfiles) > 0 else None

    @classmethod
    def getMD5OfLocalFile(cls, filename):
        with open(filename, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    @classmethod
    def getMD5OfRemoteFile(cls, location, proxy = None):
        if isinstance(proxy, str):
            proxy = { "https": proxy, "http": proxy }
        resp = requests.get(location, proxies = proxy, verify = False, timeout = 5)
        resp.raise_for_status()
        return hashlib.md5(resp.content).hexdigest()
