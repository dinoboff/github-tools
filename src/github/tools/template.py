"""
Template for for PasteScript
"""
from datetime import date
from paste.script.templates import var
from paste.script.templates import Template

YEAR = date.today().year

LICENCE_HEADER ="""%(description)s

Copyright (c) %(year)s, %(author)s
All rights reserved.

"""

GPL = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU%(gpl_type)s General Public License as published by
the Free Software Foundation, either version %(gpl_version)s of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU%(gpl_type)s General Public License for more details.

You should have received a copy of the GNU%(gpl_type)s General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

BSD = """
Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the %(org)s nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


class GithubTemplate(Template):
    """Buildout template"""
    _template_dir = 'tmpl/gh'
    summary = "A basic layout for project hosted on GitHub"
    use_cheetah = True
    vars = [
        var('package', 'The package contained',
            default='example'),
        var('description',
            'One-line description of the package',
            default='<On-line description>'),
        var('licence',
            'package licence - GPLv2/GPLv3/LGPLv2/LGPLv3/AGPLv3/BSD',
            default='GPLv3'),
        var('author', 'Author name', '<Author>'),
        var('author_email', 'Author email'),
        var('org', 'Organisation name - for licence.', default='<Organisation>'),
        ]
    def check_vars(self, vars, command):    
        if not command.options.no_interactive and \
           not hasattr(command, '_deleted_once'):
            del vars['package']
            command._deleted_once = True
        return Template.check_vars(self, vars, command)
    
    def pre(self, command, output_dir, vars):
        vars['year'] = YEAR    
        licence = vars.get('licence')
        vars['licence_body'] = ''
        print 'licence: ', licence
        if licence:
            if licence == 'BSD':
                licence_tmpl = BSD
            elif licence == 'LGPLv2':
                vars['gpl_type'] = ' Lesser'
                vars['gpl_version'] = '2'
                vars['licence'] = 'LGPLv2'
                licence_tmpl = GPL
            elif licence == 'LGPLv3':
                vars['gpl_type'] = ' Lesser'
                vars['gpl_version'] = '3'
                vars['licence'] = 'LGPLv3'
                licence_tmpl = GPL
            elif licence == 'AGPLv3':
                vars['gpl_type'] = ' Affero'
                vars['gpl_version'] = '3'
                vars['licence'] = 'AGPLv3'
                licence_tmpl = GPL
            elif licence == 'GPLv2':
                vars['gpl_type'] = ''
                vars['gpl_version'] = '2'
                vars['licence'] = 'GPLv2'
                licence_tmpl = GPL
            else:
                vars['gpl_type'] = ''
                vars['gpl_version'] = '3'
                vars['licence'] = 'GPL'
                licence_tmpl = GPL
            vars['licence_body'] = (LICENCE_HEADER + licence_tmpl) % vars