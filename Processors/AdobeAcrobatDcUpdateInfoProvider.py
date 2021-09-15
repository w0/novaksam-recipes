#!/usr/bin/python
#
# Copyright 2014: wycomco GmbH (choules@wycomco.de)
#           2015: modifications by Tim Sutton
# 			2015: modifications by Sam Novak
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for AdobeAcrobatDcUpdateInfoProvider class"""
# Disabling warnings for env members and imports that only affect recipe-
# specific processors.
# pylint: disable=e1101

from __future__ import absolute_import

from autopkglib import Processor, ProcessorError, URLGetter

__all__ = ["AdobeAcrobatDcUpdateInfoProvider"]

MAJOR_VERSION_DEFAULT = "AcrobatDC"
CHECK_OS_VERSION_DEFAULT = "10.13"
# https://ardownload2.adobe.com/pub/adobe/reader/mac/AcrobatDC/2100120145/AcroRdrDC_2100120145_MUI.dmg
# https://sstats.adobe.com/ee/v1/interact?configId=11dd9af9-1455-4159-bb5e-0b1fdf039f76:prod&requestId=d3354307-9e9b-4049-ac00-5255c845ab62
# https://sstats.adobe.com/ee/v1/interact?configId=11dd9af9-1455-4159-bb5e-0b1fdf039f76:prod&requestId=d3354307-9e9b-4049-ac00-5255c845ab62
AR_UPDATER_DOWNLOAD_URL = (
    "https://ardownload2.adobe.com/pub/adobe/acrobat/mac/%s/%s/%sUpd%s.dmg"
)

AR_UPDATER_BASE_URL = "https://armmf.adobe.com/arm-manifests/mac"
AR_URL_TEMPLATE = "/%s/acrobat/current_version.txt"
AR_MAJREV_IDENTIFIER = "{MAJREV}"
OSX_MAJREV_IDENTIFIER = "{OS_VER_MAJ}"
OSX_MINREV_IDENTIFIER = "{OS_VER_MIN}"


class AdobeAcrobatDcUpdateInfoProvider(URLGetter):
    """Provides URL to the latest Adobe Reader release."""

    description = __doc__
    input_variables = {
        "major_version": {
            "required": False,
            "description": (
                "Major version. Examples: 'AcrobatDC', 'Acrobat2015'. Defaults to "
                "%s" % MAJOR_VERSION_DEFAULT
            ),
        },
        "os_version": {
            "required": False,
            "default": CHECK_OS_VERSION_DEFAULT,
            "description": (
                "Version of OS X to check. Default: %s" % CHECK_OS_VERSION_DEFAULT
            ),
        },
    }
    output_variables = {
        "url": {"description": "URL to the latest Adobe Reader release.",},
        "version": {"description": "Version for this update.",},
    }

    def get_reader_updater_dmg_url(self, major_version):
        """Returns download URL for Adobe Reader Updater DMG"""

        try:
            version_string = self.download(
                AR_UPDATER_BASE_URL + AR_URL_TEMPLATE % major_version, text=True
            )
        except Exception as err:
            raise ProcessorError("Can't open URL template: %s" % (err))
        version_string = version_string.replace(AR_MAJREV_IDENTIFIER, major_version)

        versioncode = version_string.replace(".", "")
        versioncode = versioncode.replace("\n","")
    
        url = AR_UPDATER_DOWNLOAD_URL % (
            major_version,
            versioncode,
            major_version,
            versioncode,
        )

        return (url, version_string)

    def main(self):
        major_version = self.env.get("major_version", MAJOR_VERSION_DEFAULT)

        (url, version) = self.get_reader_updater_dmg_url(major_version)

        self.env["url"] = url
        self.env["version"] = version

        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    PROCESSOR = AdobeAcrobatDcUpdateInfoProvider()
    PROCESSOR.execute_shell()
