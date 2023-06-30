# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

#########Edit by Adyant for faster import###########
import sys
import mock
#For importing pyiron_base.cli
sys.modules['pint'] = mock.MagicMock()
sys.modules['git'] = mock.MagicMock()
#For importing pyiron.Project
sys.modules['mendeleev'] = mock.MagicMock()
sys.modules['mp_api.client'] = mock.MagicMock()
sys.modules['seaborn'] = mock.MagicMock()
sys.modules['nglview'] = mock.MagicMock()
#Make it even faster
sys.modules['structuretoolkit'] = mock.MagicMock()
sys.modules['structuretoolkit.analyse'] = mock.MagicMock()
sys.modules['structuretoolkit.visualize'] = mock.MagicMock()
sys.modules['structuretoolkit.common'] = mock.MagicMock()
sys.modules['structuretoolkit.build'] = mock.MagicMock()
sys.modules['structuretoolkit.common.error'] = mock.MagicMock()
sys.modules['pymatgen.io.ase'] = mock.MagicMock()
sys.modules['pymatgen.core'] = mock.MagicMock()
sys.modules['ase.io'] = mock.MagicMock()
sys.modules['ase.spacegroup'] = mock.MagicMock()
sys.modules['ase.build'] = mock.MagicMock()
sys.modules['ase.build.bulk'] = mock.MagicMock()
#Make it blazing fast
sys.modules['matplotlib.pyplot'] = mock.MagicMock()
#####################################################

from pyiron_base.state import state

# API of the pyiron_base module - in alphabetical order
from pyiron_base.interfaces.factory import PyironFactory
from pyiron_base.storage.flattenedstorage import FlattenedStorage
from pyiron_base.storage.hdfio import FileHDFio, ProjectHDFio
from pyiron_base.storage.datacontainer import DataContainer
from pyiron_base.storage.has_stored_traits import HasStoredTraits
from pyiron_base.storage.inputlist import InputList
from pyiron_base.storage.parameters import GenericParameters
from pyiron_base.storage.filedata import load_file, FileDataTemplate, FileData
from pyiron_base.utils.deprecate import Deprecator, deprecate, deprecate_soon
from pyiron_base.utils.error import ImportAlarm
from pyiron_base.jobs.job.extension.executable import Executable
from pyiron_base.project.external import Notebook, load, dump
from pyiron_base.jobs.job.generic import GenericJob
from pyiron_base.jobs.job.interactive import InteractiveBase
from pyiron_base.jobs.master.interactivewrapper import InteractiveWrapper
from pyiron_base.jobs.job.extension.jobstatus import (
    JobStatus,
    job_status_successful_lst,
    job_status_finished_lst,
    job_status_lst,
)
from pyiron_base.jobs.job.jobtype import JOB_CLASS_DICT, JobType, JobTypeChoice
from pyiron_base.jobs.job.template import TemplateJob, PythonTemplateJob
from pyiron_base.jobs.job.factory import JobFactoryCore
from pyiron_base.jobs.master.generic import GenericMaster, get_function_from_string
from pyiron_base.jobs.master.list import ListMaster
from pyiron_base.jobs.master.parallel import ParallelMaster, JobGenerator
from pyiron_base.jobs.master.serial import SerialMasterBase
from pyiron_base.jobs.master.flexible import FlexibleMaster
from pyiron_base.project.generic import Project, Creator
from pyiron_base.utils.parser import Logstatus, extract_data_from_file
from pyiron_base.jobs.job.extension.server.queuestatus import validate_que_request
from pyiron_base.state.settings import Settings
from pyiron_base.state.install import install_dialog
from pyiron_base.jobs.datamining import PyironTable, TableJob
from pyiron_base.interfaces.object import HasDatabase, HasStorage, PyironObject
from pyiron_base.database.performance import get_database_statistics
from pyiron_base.interfaces.has_groups import HasGroups
from pyiron_base.interfaces.has_hdf import HasHDF

from pyiron_base.jobs.job.toolkit import Toolkit, BaseTools

Project.register_tools("base", BaseTools)

#########Edit by Adyant for faster import###########
# optional API of the pyiron_base module
# try:
#     from pyiron_base.project.gui import ProjectGUI
# except (ImportError, TypeError, AttributeError):
#     pass
#####################################################

# Internal init
from ._version import get_versions
from pyiron_base.utils.jedi import fix_ipython_autocomplete

# Set version of pyiron_base
__version__ = get_versions()["version"]
del get_versions

# Jedi fix
fix_ipython_autocomplete()
