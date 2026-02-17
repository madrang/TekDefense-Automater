"""
The outputs.py module represents some form of all outputs from the Automater program to include all variation of output files.
Any addition to the Automater that brings any other output requirement should be programmed in this module.

Class(es):
    SiteDetailOutput -- Wrapper class around all functions that print output from Automater,
                        to include standard output and file system output.

Function(s):
    No global exportable functions are defined.

Exception(s):
    No exceptions exported.
"""
import csv
import socket
import re
from datetime import datetime
from operator import attrgetter

class SiteDetailOutput:
    """ SiteDetailOutput provides the capability to output information
            to the screen, a text file, a comma-seperated value file, or an html file.

    Public Method(s):
        createOutputInfo

    Instance variable(s):
        _listofsites - list storing the list of site results stored.
    """

    def __init__(self,sitelist):
        """ Class constructor.
            Stores the incoming list of sites in the _listofsites list.

        Argument(s):
            sitelist -- list containing site result information to be printed.
        """
        self._listofsites = []
        self._listofsites = sitelist

    @property
    def ListOfSites(self):
        """ Checks instance variable _listofsites for content.
            Returns _listofsites if it has content or None if it does not.

        Return value(s):
            _listofsites -- list containing list of site results if variable contains data.
            None -- if _listofsites is empty or not assigned.
        """
        if self._listofsites is None or len(self._listofsites) == 0:
            return None
        return self._listofsites

    def createOutputInfo(self,parser):
        """ Checks parser information calls correct print methods based on parser requirements.

        Argument(s):
            parser -- Parser object storing program input parameters used when program was run.

        Return value(s):
            Nothing is returned from this Method.
        """
        self.PrintToScreen(parser.hasBotOut)
        if parser.CEFOutFile:
            self.PrintToCEFFile(parser.CEFOutFile)
        if parser.TextOutFile:
            self.PrintToTextFile(parser.TextOutFile)
        if parser.HTMLOutFile:
            self.PrintToHTMLFile(parser.HTMLOutFile)
        if parser.CSVOutFile:
            self.PrintToCSVFile(parser.CSVOutFile)

    def PrintToScreen(self, printinbotformat):
        """ Calls correct function to ensure site information is printed to the user's standard output correctly.

        Argument(s):
            printinbotformat -- True or False argument representing minimized output. True if minimized requested.

        Return value(s):
            Nothing is returned from this Method.
        """
        if printinbotformat:
            self.PrintToScreenBot()
        else:
            self.PrintToScreenNormal()

    def PrintToScreenBot(self):
        """ Formats site information minimized and prints it to the user's standard output.

        Argument(s):
            No arguments are required.

        Return value(s):
            Nothing is returned from this Method.
        """
        sites = sorted(self.ListOfSites, key=attrgetter("Target"))
        if sites is None:
            print("No sites results!")
            return
        target = ""
        for site in sites:
            if not isinstance(site.RegEx, str):  # this is a multisite
                for index in range(len(site.RegEx)):  # the regexs will ensure we have the exact number of lookups
                    site_importantProperty = site.getImportantProperty(index)
                    if target != site.Target:
                        print(f"\n**_ Results found for: {site.Target} _**")
                        target = site.Target
                        # Check for them ALL to be None or 0 length
                    sourceurlhasnoreturn = True
                    for answer in site_importantProperty:
                        if answer is not None:
                            if len(answer) > 0:
                                sourceurlhasnoreturn = False

                    if sourceurlhasnoreturn:
                        print(f"[+] {site.SourceURL} No results found")
                        break
                    else:
                        if site_importantProperty is None or len(site_importantProperty) == 0:
                            print(f"No results in the {site.FriendlyName[index]} category")
                        else:
                            if site_importantProperty[index] is None or len(site_importantProperty[index]) == 0:
                                print(f"{site.ReportStringForResult[index]} No results found")
                            else:
                                # if it's just a string we don't want it output like a list
                                if isinstance(site_importantProperty[index], str):
                                    print(f"{site.ReportStringForResult[index]} {
                                            str(site_importantProperty)
                                                .replace("www.", "www[.]")
                                                .replace("http", "hxxp")
                                        }")
                                # must be a list since it failed the isinstance check on string
                                else:
                                    laststring = ""
                                    for siteresult in site_importantProperty[index]:
                                        if f"{site.ReportStringForResult[index]} {siteresult}" != laststring:
                                            print(f"{site.ReportStringForResult[index]} {
                                                    str(siteresult)
                                                        .replace("www.", "www[.]")
                                                        .replace("http", "hxxp")
                                                }")
                                            laststring = f"{site.ReportStringForResult[index]} {siteresult}"
            else: # this is a singlesite
                site_importantProperty = site.getImportantProperty()
                if target != site.Target:
                    print(f"\n**_ Results found for: {site.Target} _**")
                    target = site.Target
                if site_importantProperty is None or len(site_importantProperty) == 0:
                    print(f"[+] {site.FriendlyName} No results found")
                else:
                    #if it's just a string we don't want it output like a list
                    if isinstance(site_importantProperty, str):
                        print(f"{site.ReportStringForResult} {
                            str(site_importantProperty)
                                .replace("www.", "www[.]")
                                .replace("http", "hxxp")
                            }")
                    else: # must be a list since it failed the isinstance check on string
                        laststring = ""
                        for siteresult in site_importantProperty:
                            if f"{site.ReportStringForResult} {siteresult}" != laststring:
                                print(f"{site.ReportStringForResult} {
                                    str(siteresult)
                                        .replace("www.", "www[.]")
                                        .replace("http", "hxxp")
                                    }")
                                laststring = f"{site.ReportStringForResult} {siteresult}"

    def PrintToScreenNormal(self):
        """ Formats site information correctly and prints it to the user's standard output.

        Argument(s):
            No arguments are required.

        Return value(s):
            Nothing is returned from this Method.
        """
        sites = sorted(self.ListOfSites, key=attrgetter("Target"))
        target = ""
        if sites is not None:
            for site in sites:
                if not isinstance(site.RegEx, str):  # this is a multisite
                    for index in range(len(site.RegEx)):  # the regexs will ensure we have the exact number of lookups
                        site_importantProperty = site.getImportantProperty(index)
                        if target != site.Target:
                            print(f"\n____________________     Results found for: {site.Target}     ____________________")
                            target = site.Target
                        if site_importantProperty is None or len(site_importantProperty) == 0:
                            print(f"No results in the {site.FriendlyName[index]} category")
                        else:
                            if site_importantProperty[index] is None or len(site_importantProperty[index]) == 0:
                                print(f"{site.ReportStringForResult[index]} No results found")
                            else:
                                # if it's just a string we don't want it output like a list
                                if isinstance(site_importantProperty[index], str):
                                    print(f"{site.ReportStringForResult[index]} {
                                                str(site_importantProperty)
                                                    .replace("www.", "www[.]")
                                                    .replace("http", "hxxp")
                                            }")
                                else: # must be a list since it failed the isinstance check on string
                                    laststring = ""
                                    for siteresult in site_importantProperty[index]:
                                        if f"{site.ReportStringForResult[index]} {siteresult}" != laststring:
                                            print(f"{site.ReportStringForResult[index]} {
                                                        str(siteresult)
                                                            .replace("www.", "www[.]")
                                                            .replace("http", "hxxp")
                                                    }")
                                            laststring = f"{site.ReportStringForResult[index]} {siteresult}"
                else:  # this is a singlesite
                    site_importantProperty = site.getImportantProperty()
                    if target != site.Target:
                        print(f"\n____________________     Results found for: {site.Target}     ____________________")
                        target = site.Target
                    if site_importantProperty is None or len(site_importantProperty) == 0:
                        print(f"No results found in the {site.FriendlyName}")
                    else:
                        # if it's just a string we don't want it output like a list
                        if isinstance(site_importantProperty, str):
                            print(f"{site.ReportStringForResult} {
                                        str(site_importantProperty)
                                            .replace("www.", "www[.]")
                                            .replace("http", "hxxp")
                                    }")
                        # must be a list since it failed the isinstance check on string
                        else:
                            laststring = ""
                            for siteresult in site_importantProperty:
                                if f"{site.ReportStringForResult} {siteresult}" != laststring:
                                    print(f"{site.ReportStringForResult} {
                                            str(siteresult)
                                                .replace("www.", "www[.]")
                                                .replace("http", "hxxp")
                                        }")
                                    laststring = f"{site.ReportStringForResult} {siteresult}"

    def PrintToCEFFile(self, cefoutfile):
        """ Formats site information correctly and prints it to an output file in CEF format.
            CEF format specification from http://mita-tac.wikispaces.com/file/view/CEF+White+Paper+071709.pdf
            "Jan 18 11:07:53 host message"
        where message:
            "CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension"

        Argument(s):
            cefoutfile -- A string representation of a file that will store the output.

        Return value(s):
            Nothing is returned from this Method.
        """
        sites = sorted(self.ListOfSites, key = attrgetter("Target"))
        cef_Severity = "2"
        cef_fields = [
            " ".join([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              , socket.gethostname()
               ])                               # Prefix
            , "CEF:Version1.1"                  # CEF Version
            , "TekDefense"                      # Vendor
            , "Automater"                       # Product
            , "2.1"                             # Version
            , "0"                               # SignatureID
        ]
        pattern = r"^\[\+\]\s+"
        target = ""
        print(f"\n[+] Generating CEF output: {cefoutfile}")
        f = open(cefoutfile, "w")
        csv.register_dialect("escaped", delimiter="|", escapechar="\\", doublequote=False, quoting=csv.QUOTE_NONE)
        cefRW = csv.writer(f, "escaped")
        # cefRW.writerow(["Target", "Type", "Source", "Result"])
        if sites is not None:
            for site in sites:
                cef_kwargs = {
                    "tgt": site.Target
                    , "typ": site.TargetType
                }
                if not isinstance(site.RegEx, str):  # this is a multisite:
                    for index in range(len(site.RegEx)):  # the regexs will ensure we have the exact number of lookups
                        site_importantProperty = site.getImportantProperty(index)
                        if site_importantProperty is None or len(site_importantProperty) == 0:
                            cef_kwargs["src"] = site.FriendlyName[index]
                            cef_kwargs["res"] = "No results found"
                            cefRW.writerow(cef_fields + [f"[{",".join(
                                            [f"{key}={value}" for key, value in cef_kwargs.items()]
                                        )}]"
                                        , 1
                                        , site.Target
                                    ]
                                )
                        else:
                            if site_importantProperty[index] is None or len(site_importantProperty[index]) == 0:
                                cef_kwargs["src"] = site.FriendlyName[index]
                                cef_kwargs["res"] = "No results found"
                                cefRW.writerow(cef_fields + [f"[{",".join(
                                                [f"{key}={value}" for key, value in cef_kwargs.items()]
                                            )}]"
                                            , 1
                                            , site.Target
                                        ]
                                    )
                            else:
                                # if it's just a string we don't want it to output like a list
                                if isinstance(site_importantProperty, str):
                                    cef_kwargs["src"] = site.FriendlyName
                                    cef_kwargs["res"] = site_importantProperty
                                    cefRW.writerow(cef_fields + [f"[{",".join(
                                                    [f"{key}={value}" for key, value in cef_kwargs.items()]
                                                )}] {re.sub(pattern, "", site.ReportStringForResult[index])}{site_importantProperty}"
                                                , cef_Severity
                                                , site.Target
                                            ]
                                        )

                                else: # must be a list since it failed the isinstance check on string
                                    laststring = ""
                                    for siteresult in site_importantProperty[index]:
                                        cef_kwargs["src"] = site.FriendlyName[index]
                                        cef_kwargs["res"] = siteresult
                                        if f"{site.Target}{site.TargetType}{site.FriendlyName[index]}{siteresult}" != laststring:
                                            cefRW.writerow(cef_fields + [f"[{",".join(
                                                            [f"{key}={value}" for key, value in cef_kwargs.items()]
                                                        )}] {re.sub(pattern, "", site.ReportStringForResult[index])}{siteresult}"
                                                        , cef_Severity
                                                        , site.Target
                                                    ]
                                                )
                                            laststring = f"{site.Target}{site.TargetType}{site.FriendlyName[index]}{siteresult}"
                else: # this is a singlesite
                    site_importantProperty = site.getImportantProperty()
                    if site_importantProperty is None or len(site_importantProperty) == 0:
                        cef_kwargs["src"] = site.FriendlyName
                        cef_kwargs["res"] = "No results found"
                        cefRW.writerow(cef_fields + [f"[{",".join(
                                [f"{key}={value}" for key, value in cef_kwargs.items()])}]"
                            , "1"
                            , site.Target
                        ])
                    else:
                        if isinstance(site_importantProperty, str): # if it's just a string we don't want it output like a list
                            cef_kwargs["src"] = site.FriendlyName
                            cef_kwargs["res"] = site_importantProperty
                            cefRW.writerow(cef_fields + [f"[{",".join(
                                            [f"{key}={value}" for key, value in cef_kwargs.items()]
                                        )}] {re.sub(pattern, "", site.ReportStringForResult)}{site_importantProperty}"
                                        , cef_Severity
                                        , site.Target
                                    ]
                                )
                        else:
                            laststring = ""
                            for siteresult in site_importantProperty:
                                cef_kwargs["src"] = site.FriendlyName
                                cef_kwargs["res"] = siteresult
                                if f"{site.Target}{site.TargetType}{site.FriendlyName}{siteresult}" != laststring:
                                    cefRW.writerow(cef_fields + [f"[{",".join(
                                                    [f"{key}={value}" for key, value in cef_kwargs.items()]
                                                )}] {re.sub(pattern, "", site.ReportStringForResult)}{site_importantProperty}"
                                                , cef_Severity
                                                , site.Target
                                            ]
                                        )
                                    laststring = f"{site.Target}{site.TargetType}{site.FriendlyName}{siteresult}"
        f.flush()
        f.close()
        print(f"{cefoutfile} Generated")

    def PrintToTextFile(self,textoutfile):
        """ Formats site information correctly and prints it to an output file in text format.

        Argument(s):
            textoutfile -- A string representation of a file that will store the output.

        Return value(s):
            Nothing is returned from this Method.
        """
        sites = sorted(self.ListOfSites, key = attrgetter("Target"))
        target = ""
        print(f"\n[+] Generating text output: {textoutfile}")
        f = open(textoutfile, "w")
        if sites is not None:
            for site in sites:
                if not isinstance(site.RegEx, str): # this is a multisite
                    for index in range(len(site.RegEx)): # the regexs will ensure we have the exact number of lookups
                        site_importantProperty = site.getImportantProperty(index)
                        if target != site.Target:
                            f.write(f"\n____________________     Results found for: {site.Target}     ____________________")
                            target = site.Target
                        if site_importantProperty is None or len(site_importantProperty)==0:
                            f.write(f"\nNo results in the {site.FriendlyName[index]} category")
                        else:
                            if site_importantProperty[index] is None or len(site_importantProperty[index]) == 0:
                                f.write(f"\n{site.ReportStringForResult[index]} No results found")
                            else:
                                # if it's just a string we don't want it to output like a list
                                if isinstance(site_importantProperty[index], str):
                                    f.write(f"\n{site.ReportStringForResult[index]} {site_importantProperty}")
                                else: # must be a list since it failed the isinstance check on string
                                    laststring = ""
                                    for siteresult in site_importantProperty[index]:
                                        if f"{site.ReportStringForResult[index]} {siteresult}" != laststring:
                                            f.write(f"\n{site.ReportStringForResult[index]} {siteresult}")
                                            laststring = f"{site.ReportStringForResult[index]} {siteresult}"
                else: # this is a singlesite
                    site_importantProperty = site.getImportantProperty()
                    if target != site.Target:
                        f.write(f"\n____________________     Results found for: {site.Target}     ____________________")
                        target = site.Target
                    if site_importantProperty is None or len(site_importantProperty) == 0:
                        f.write(f"\nNo results found in the {site.FriendlyName}")
                    else: # if it's just a string we don't want it output like a list
                        if isinstance(site_importantProperty, str):
                            f.write(f"\n{site.ReportStringForResult} {site_importantProperty}")
                        else:
                            laststring = ""
                            for siteresult in site_importantProperty:
                                if f"{site.ReportStringForResult} {siteresult}" != laststring:
                                    f.write(f"\n{site.ReportStringForResult} {siteresult}")
                                    laststring = f"{site.ReportStringForResult} {siteresult}"
        f.flush()
        f.close()
        print(f"{textoutfile} Generated")

    def PrintToCSVFile(self,csvoutfile):
        """ Formats site information correctly and prints it to an output file with comma-seperators.

        Argument(s):
            csvoutfile -- A string representation of a file that will store the output.

        Return value(s):
            Nothing is returned from this Method.
        """
        sites = sorted(self.ListOfSites, key=attrgetter("Target"))
        target = ""
        print(f"\n[+] Generating CSV output: {csvoutfile}")
        f = open(csvoutfile, "w")
        csvRW = csv.writer(f, quoting=csv.QUOTE_ALL)
        csvRW.writerow(["Target", "Type", "Source", "Result"])
        if sites is not None:
            for site in sites:
                data_arr = [ site.Target, site.TargetType, None, None ]
                if not isinstance(site.RegEx, str): #this is a multisite:
                    for index in range(len(site.RegEx)): #the regexs will ensure we have the exact number of lookups
                        site_importantProperty = site.getImportantProperty(index)
                        if site_importantProperty is None or len(site_importantProperty)==0:
                            data_arr[2] = site.FriendlyName[index]
                            data_arr[3] = "No results found"
                            csvRW.writerow(data_arr)
                        else:
                            if site_importantProperty[index] is None or len(site_importantProperty[index])==0:
                                data_arr[2] = site.FriendlyName[index]
                                data_arr[3] = "No results found"
                                csvRW.writerow(data_arr)
                            else: # if it's just a string we don't want it to output like a list
                                if isinstance(site_importantProperty, str):
                                    data_arr[2] = site.FriendlyName
                                    data_arr[3] = site_importantProperty
                                    csvRW.writerow(data_arr)
                                #must be a list since it failed the isinstance check on string
                                else:
                                    laststring = ""
                                    for siteresult in site_importantProperty[index]:
                                        data_arr[2] = site.FriendlyName[index]
                                        data_arr[3] = str(siteresult)
                                        if "".join(data_arr) != laststring:
                                            csvRW.writerow(data_arr)
                                            laststring = "".join(data_arr)
                else: # this is a singlesite
                    site_importantProperty = site.getImportantProperty()
                    if site_importantProperty is None or len(site_importantProperty)==0:
                        data_arr[2] = site.FriendlyName
                        data_arr[3] = "No results found"
                        csvRW.writerow(data_arr)
                    else:
                        #if it's just a string we don't want it output like a list
                        if isinstance(site_importantProperty, str):
                            data_arr[2] = site.FriendlyName
                            data_arr[3] = site_importantProperty
                            csvRW.writerow(data_arr)
                        else:
                            laststring = ""
                            for siteresult in site_importantProperty:
                                data_arr[2] = site.FriendlyName
                                data_arr[3] = str(siteresult)
                                if "".join(data_arr) != laststring:
                                    csvRW.writerow(data_arr)
                                    laststring = "".join(data_arr)
        f.flush()
        f.close()
        print(f"{csvoutfile} Generated")

    def PrintToHTMLFile(self, htmloutfile):
        """ Formats site information correctly and prints it to an output file using HTML markup.

        Argument(s):
            htmloutfile -- A string representation of a file that will store the output.

        Return value(s):
            Nothing is returned from this Method.
        """
        sites = sorted(self.ListOfSites, key=attrgetter("Target"))
        target = ""
        print(f"\n[+] Generating HTML output: {htmloutfile}")
        f = open(htmloutfile, "w")
        f.write(self.getHTMLOpening())
        if sites is not None:
            for site in sites:
                if not isinstance(site.RegEx, str): # this is a multisite:
                    for index in range(len(site.RegEx)): # the regexs will ensure we have the exact number of lookups
                        site_importantProperty = site.getImportantProperty(index)
                        if site_importantProperty is None or len(site_importantProperty) == 0:
                            f.write(f"<tr><td>{site.Target}</td><td>{site.TargetType}</td><td>{site.FriendlyName[index]}</td><td>No results found</td></tr>\n")
                        else:
                            if site_importantProperty[index] is None or len(site_importantProperty[index]) == 0:
                                f.write(f"<tr><td>{site.Target}</td><td>{site.TargetType}</td><td>{site.FriendlyName[index]}</td><td>No results found</td></tr>\n")
                            else:
                                # if it's just a string we don't want it to output like a list
                                if isinstance(site_importantProperty, str):
                                    f.write(f"<tr><td>{site.Target}</td><td>{site.TargetType}</td><td>{site.FriendlyName}</td><td>{site_importantProperty}</td></tr>\n")
                                else:
                                    for siteresult in site_importantProperty[index]:
                                        f.write(f"<tr><td>{site.Target}</td><td>{site.TargetType}</td><td>{site.FriendlyName[index]}</td><td>{siteresult}</td></tr>\n")
                else:  # this is a singlesite
                    site_importantProperty = site.getImportantProperty()
                    if site_importantProperty is None or len(site_importantProperty) == 0:
                        f.write(f"<tr><td>{site.Target}</td><td>{site.TargetType}</td><td>{site.FriendlyName}</td><td>No results found</td></tr>\n")
                    else:
                        # if it's just a string we don't want it output like a list
                        if isinstance(site_importantProperty, str):
                            f.write(f"<tr><td>{site.Target}</td><td>{site.TargetType}</td><td>{site.FriendlyName}</td><td>{site_importantProperty}</td></tr>\n")
                        else:
                            for siteresult in site_importantProperty:
                                f.write(f"<tr><td>{site.Target}</td><td>{site.TargetType}</td><td>{site.FriendlyName}</td><td>{siteresult}</td></tr>\n")
        f.write(self.getHTMLClosing())
        f.flush()
        f.close()
        print(f"{htmloutfile} Generated")

    def getHTMLOpening(self):
        """ Creates HTML markup to provide correct formatting for initial HTML file requirements.

        Argument(s):
            No arguments required.

        Return value(s):
            string -- contains opening HTML markup information for HTML output file.
        """
        return """<style type="text/css">
    #table-3 {
        border: 1px solid #DFDFDF;
        background-color: #F9F9F9;
        width: 100%;
        -moz-border-radius: 3px;
        -webkit-border-radius: 3px;
        border-radius: 3px;
        font-family: Arial,"Bitstream Vera Sans",Helvetica,Verdana,sans-serif;
        color: #333;
    }
    #table-3 td, #table-3 th {
        border-top-color: white;
        border-bottom: 1px solid #DFDFDF;
        color: #555;
    }
    #table-3 th {
        text-shadow: rgba(255, 255, 255, 0.796875) 0px 1px 0px;
        font-family: Georgia,"Times New Roman","Bitstream Charter",Times,serif;
        font-weight: normal;
        padding: 7px 7px 8px;
        text-align: left;
        line-height: 1.3em;
        font-size: 14px;
    }
    #table-3 td {
        font-size: 12px;
        padding: 4px 7px 2px;
        vertical-align: top;
    }res
    h1 {
        text-shadow: rgba(255, 255, 255, 0.796875) 0px 1px 0px;
        font-family: Georgia,"Times New Roman","Bitstream Charter",Times,serif;
        font-weight: normal;
        padding: 7px 7px 8px;
        text-align: Center;
        line-height: 1.3em;
        font-size: 40px;
    }
    h2 {
        text-shadow: rgba(255, 255, 255, 0.796875) 0px 1px 0px;
        font-family: Georgia,"Times New Roman","Bitstream Charter",Times,serif;
        font-weight: normal;
        padding: 7px 7px 8px;
        text-align: left;
        line-height: 1.3em;
        font-size: 16px;
    }
    h4 {
        text-shadow: rgba(255, 255, 255, 0.796875) 0px 1px 0px;
        font-family: Georgia,"Times New Roman","Bitstream Charter",Times,serif;
        font-weight: normal;
        padding: 7px 7px 8px;
        text-align: left;
        line-height: 1.3em;
        font-size: 10px;
    }
</style>
<html>
    <body>
        <title> Automater Results </title>
        <h1> Automater Results </h1>
        <table id="table-3">
            <tr>
            <th>Target</th>
            <th>Type</th>
            <th>Source</th>
            <th>Result</th>
            </tr>
"""

    def getHTMLClosing(self):
        """ Creates HTML markup to provide correct formatting for closing HTML file requirements.

        Argument(s):
            No arguments required.

        Return value(s):
            string -- contains closing HTML markup information for HTML output file.
        """
        return """        </table>
        <br><br>
        <p>Created using Automater.py <a href="https://github.com/madrang/MadDefense-Automater">https://github.com/madrang/MadDefense-Automater</a></p>
    </body>
</html>"""
