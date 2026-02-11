#!/usr/bin/python3
"""
The Automater.py module defines the main() function for Automater.

Parameter Required is:
target -- List one IP Address (CIDR or dash notation accepted), URL or Hash
to query or pass the filename of a file containing IP Address info, URL or
Hash to query each separated by a newline.

Optional Parameters are:
-o, --output -- This option will output the results to a file.
-b, --bot -- This option will output minimized results for a bot.
-f, --cef -- This option will output the results to a CEF formatted file.
-w, --web -- This option will output the results to an HTML file.
-c, --csv -- This option will output the results to a CSV file.
-d, --delay -- Change the delay to the inputted seconds. Default is 2.
-s, --source -- Will only run the target against a specific source engine
to pull associated domains. Options are defined in the name attribute of
the site element in the XML configuration file. This can be a list of names separated by a semicolon.
--proxy -- This option will set a proxy (eg. proxy.example.com:8080)
-a --useragent -- Will set a user-agent string in the header of a web request.
is set by default to Automater/version#
-V, --vercheck -- This option checks and reports versioning for Automater. Checks each python
module in the Automater scope.  Default, (no -V) is False
-r, --refreshxml -- This option refreshes the tekdefense.xml file from the remote GitHub site.
Default (no -r) is False.
-v, --verbose -- This option prints messages to the screen. Default (no -v) is False.

Class(es):
No classes are defined in this module.

Function(s):
main -- Provides the instantiation point for Automater.

Exception(s):
No exceptions exported.

Fork of https://github.com/1aN0rmus/TekDefense-Automater
By ian.ahl@tekdefense.com
"""
import sys
from siteinfo import SiteFacade, Site
from utilities import Parser, IPWrapper
from outputs import SiteDetailOutput
from inputs import TargetFile

__VERSION__ = "0.1.1"
__GITLOCATION__ = "https://github.com/madrang/TekDefense-Automater"
__GITFILEPREFIX__ = "https://raw.githubusercontent.com/madrang/TekDefense-Automater/master/"

class Automater():
    def __init__(self, Proxy=None):
        self.sourcelist = ["allsources"]
        self.Proxy = Proxy
        self.Verbose = False
        self.VersionCheck = False
        self.UserAgent = "CITDB/1.0"
        self.hasBotOut = True
        self.RefreshRemoteXML = False
        self.Delay = 2                          # Delay used for accessing sites.

    def GetResults(self, targets):
        targetlist = []
        for tgt in targets:
            tgt = tgt.replace("[.]", ".").replace("{.}", ".").replace("(.)", ".")
            if IPWrapper.isIPorIPList(tgt):
                for targ in IPWrapper.getTarget(tgt):
                    targetlist.append(targ)
            else:
                targetlist.append(tgt)

        sitefac = SiteFacade(self.Verbose)
        sitefac.runSiteAutomation(self.Delay, self.Proxy, targetlist, self.sourcelist, self.UserAgent, self.hasBotOut
                                , self.RefreshRemoteXML, __GITLOCATION__)

        sites = sorted(sitefac.Sites, key=attrgetter("Target"))
        if sites is None:
            return []

        resultList = []
        for site in sites:
            if not isinstance(site._regex, str): # this is a multisite:
                for index in range(len(site.RegEx)): # the regexs will ensure we have the exact number of lookups
                    site_importantProperty = site.getImportantProperty(index)
                    if site_importantProperty is None or len(site_importantProperty) == 0:
                        continue
                    if site_importantProperty[index] is None or len(site_importantProperty[index]) == 0:
                        continue
                    # if it's just a string we don't want it to output like a list
                    if isinstance(site_importantProperty, str):
                        typ = site.TargetType
                        source = site.FriendlyName
                        res = site_importantProperty
                        resultList.append([ site.Target, typ, site.FriendlyName, res ])
                    else: # must be a list since it failed the isinstance check on string
                        laststring = ""
                        for siteresult in site_importantProperty[index]:
                            typ = site.TargetType
                            source = site.FriendlyName[index]
                            res = siteresult
                            if "" + site.Target + typ + source + str(res) != laststring:
                                resultList.append([ site.Target, typ, source, res ])
                                laststring = "" + site.Target + typ + source + str(res)
            else: # this is a singlesite
                site_importantProperty = site.getImportantProperty()
                if site_importantProperty is None or len(site_importantProperty) == 0:
                    continue
                # if it's just a string we don't want it output like a list
                if isinstance(site_importantProperty, str):
                    typ = site.TargetType
                    source = site.FriendlyName
                    res = site_importantProperty
                    resultList.append([ site.Target, typ, source, res ])
                else:
                    laststring = ""
                    for siteresult in site_importantProperty:
                        typ = site.TargetType
                        source = site.FriendlyName
                        res = siteresult
                        if "" + site.Target + typ + source + str(res) != laststring:
                            resultList.append([ site.Target, typ, source, res ])
                            laststring = "" + site.Target + typ + source + str(res)
        return resultList

def main():
    """
    Serves as the instantiation point to start Automater.

    Argument(s):
    No arguments are required.

    Return value(s):
    Nothing is returned from this Method.

    Restriction(s):
    The Method has no restrictions.
    """

    sites = []
    parser = Parser("IP, URL, and Hash Passive Analysis tool", __VERSION__)

    # if no target run and print help
    if not parser.hasTarget():
        print("[!] No argument given.")
        parser.print_help()  # need to fix this. Will later
        sys.exit()

    if parser.VersionCheck:
        Site.checkmoduleversion(__GITFILEPREFIX__, __GITLOCATION__, parser.Proxy, parser.Verbose)

    # user may only want to run against one source - allsources
    # is the seed used to check if the user did not enter an s tag
    sourcelist = ["allsources"]
    if parser.hasSource():
        sourcelist = parser.Source.split(";")

    # a file input capability provides a possibility of
    # multiple lines of targets
    targetlist = []
    if parser.hasInputFile():
        for tgtstr in TargetFile.TargetList(parser.InputFile, parser.Verbose):
            tgtstrstripped = tgtstr.replace("[.]", ".").replace("{.}", ".").replace("(.)", ".")
            if IPWrapper.isIPorIPList(tgtstrstripped):
                for targ in IPWrapper.getTarget(tgtstrstripped):
                    targetlist.append(targ)
            else:
                targetlist.append(tgtstrstripped)
    else:  # one target or list of range of targets added on console
        target = parser.Target
        tgtstrstripped = target.replace("[.]", ".").replace("{.}", ".").replace("(.)", ".")
        if IPWrapper.isIPorIPList(tgtstrstripped):
            for targ in IPWrapper.getTarget(tgtstrstripped):
                targetlist.append(targ)
        else:
            targetlist.append(tgtstrstripped)

    sitefac = SiteFacade(parser.Verbose)
    sitefac.runSiteAutomation(parser.Delay, parser.Proxy, targetlist, sourcelist, parser.UserAgent, parser.hasBotOut,
                              parser.RefreshRemoteXML, __GITLOCATION__)
    sites = sitefac.Sites
    if sites:
        SiteDetailOutput(sites).createOutputInfo(parser)

if __name__ == "__main__":
    main()
