# -*- coding: utf-8 -*-

"""
Python library for Hansight Enterprise
"""

__title__ = 'pyent'
__version__ = '0.1'
__author__ = 'Cookie Zhang'

from .asset import Asset
from .assettype import AssetType
from .eventattribute import EventAttribute
from .eventtype import EventType
from .eventbase import EventBase
from .eventparser import EventParser
from .ceptemplate import CepTemplate
from .ceprule import CepRule, CEPRuleType
from .collector import Collector
from .user import User
from .systemunit import SystemUnit
from .event import Event
from .license import License
from .alarm import Alarm
from .systemconfig import Intranet
from .systemconfig import SMTP
from .systemconfig import InitConfig
from .contexts import Contexts
from .eventanalysis import EventAnalysis
from .intelligencegroup import IntelligenceGroup
from .intelligence import Intelligence
from .attack import Attack, AttackType
from .knowledge import Knowledge, KnowledgeType
from .ceptask import CepTask
from .globaltrend import GlobalTrend
from .intelligentanalysis import IntelligentAnalysis
from .dashboard import Dashboard
from .component import Component, ComponentGroup
from .reporttemplate import ReportTemplate
from .assetview import AssetView
from .assetview import AssetBusiness
from .assetview import AssetDomain
from .assetview import AssetLocation
from .timereport import TimeReport
from .role import Role
from .auditlog import AuditLog
from .vulnerability import Vulnerability
from .dataviewer import DVCollector
from .dataviewer import DVParser
from .dataviewer import DVSource

import session


# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())


class PyEnt(object):
    def __init__(self, console_url, username=None, password=None, **kwargs):
        self._session = session.clean()
        self._console_url = console_url
        self._username = username
        self._password = password

        self._event_attribute = EventAttribute(self._console_url, self._session)
        self._event_type = EventType(self._console_url, self._session)
        self._event_base = EventBase(self._console_url, self._session)
        self._event_parser = EventParser(self._console_url, self._session)
        self._cep_rule = CepRule(self._console_url, self._session)
        self._cep_template = CepTemplate(self._console_url, self._session)
        self._collector = Collector(self._console_url, self._session)
        self._asset = Asset(self._console_url, self._session)
        self._asset_type = AssetType(self._console_url, self._session)
        self._user = User(self._console_url, self._session)
        self._system_unit = SystemUnit(self._console_url, self._session)
        self._event = Event(self._console_url, self._session)
        self._license = License(self._console_url, self._session)
        self._alarm = Alarm(self._console_url, self._session)
        self._intranet = Intranet(self._console_url, self._session)
        self._smtp = SMTP(self._console_url, self._session)
        self._cepruletype = CEPRuleType(self._console_url, self._session)
        self._contexts = Contexts(self._console_url, self._session)
        self._event_analysis = EventAnalysis(self._console_url, self._session)
        self._intelligence_group = IntelligenceGroup(self._console_url, self._session)
        self._intelligence = Intelligence(self._console_url, self._session)
        self._attack_type = AttackType(self._console_url, self._session)
        self._attack = Attack(self._console_url, self._session)
        self._knowledge_type = KnowledgeType(self._console_url, self._session)
        self._knowledge = Knowledge(self._console_url, self._session)
        self._ceptask = CepTask(self._console_url, self._session)
        self._global_trend = GlobalTrend(self._console_url, self._session)
        self._intelligent_analysis = IntelligentAnalysis(self._console_url, self._session)
        self._dashboard = Dashboard(self._console_url, self._session)
        self._component_group = ComponentGroup(self._console_url, self._session)
        self._component = Component(self._console_url, self._session)
        self._report_template = ReportTemplate(self._console_url, self._session)
        self._asset_view = AssetView(self._console_url, self._session)
        self._time_report = TimeReport(self._console_url, self._session)
        self._role = Role(self._console_url, self._session)
        self._auditlog = AuditLog(self._console_url, self._session)
        self._vulnerability = Vulnerability(self._console_url, self._session)
        self._dvcollector = DVCollector(self._console_url, self._session)
        self._dvparser = DVParser(self._console_url, self._session)
        self._dvsource = DVSource(self._console_url, self._session)
        self._asset_business = AssetBusiness(self._console_url, self._session)
        self._asset_domain = AssetDomain(self._console_url, self._session)
        self._asset_location = AssetLocation(self._console_url, self._session)
        self._init_config = InitConfig(self._console_url, self._session)

        if self._username and self._password:
            self.login()

    def login(self, username=None, password=None):
        username = username or self._username
        password = password or self._password
        self._session = session.login(self._console_url, username, password)
        self.update_session()

    def logout(self):
        self._session = session.logout(self._session)

    def update_session(self):
        self._event_parser.session = self._session
        self._event_type.session = self._session
        self._event_base.session = self._session
        self._event_attribute.session = self._session
        self._cep_rule.session = self._session
        self._cep_template.session = self._session
        self._collector.session = self._session
        self._asset.session = self._session
        self._asset_type.session = self._session
        self._user.session = self._session
        self._system_unit.session = self._session
        self._event.session = self._session
        self._license.session = self._session
        self._alarm.session = self._session
        self._intranet.session = self._session
        self._smtp.session = self._session
        self._cepruletype.session = self._session
        self._contexts.session = self._session
        self._event_analysis.session = self._session
        self._intelligence_group.session = self._session
        self._intelligence.session = self._session
        self._attack_type.session = self._session
        self._attack.session = self._session
        self._knowledge_type.session = self._session
        self._knowledge.session = self._session
        self._ceptask.session = self._session
        self._global_trend.session = self._session
        self._intelligent_analysis.session = self._session
        self._dashboard.session = self._session
        self._component.session = self._session
        self._component_group.session = self._session
        self._report_template.session = self._session
        self._asset_view.session = self._session
        self._time_report.session = self._session
        self._role.session = self._session
        self._auditlog.session = self._session
        self._vulnerability.session = self._session
        self._dvcollector.session = self._session
        self._dvparser.session = self._session
        self._dvsource.session = self._session
        self._asset_business.session = self._session
        self._asset_domain.session = self._session
        self._asset_location.session = self._session
        self._init_config.session = self._session

    def get_resource(self, resource):
        return {
            'EventAttribute': self._event_attribute,
            'EventType': self._event_type,
            'EventBase': self._event_base,
            'EventParser': self._event_parser,
            'CepTemplate': self._cep_template,
            'CepRule': self._cep_rule,
            'Collector': self._collector,
            'Asset': self._asset,
            'AssetType': self._asset_type,
            'User': self._user,
            'SystemUnit': self._system_unit,
            'Event': self._event,
            'License': self._license,
            'Alarm': self._alarm,
            'Intranet': self._intranet,
            'SMTP': self._smtp,
            'CEPRuleType': self._cepruletype,
            'Contexts': self._contexts,
            'EventAnalysis': self._event_analysis,
            'IntelligenceGroup': self._intelligence_group,
            'Intelligence': self._intelligence,
            'AttackType': self._attack_type,
            'Attack': self._attack,
            'KnowledgeType': self._knowledge_type,
            'Knowledge': self._knowledge,
            'CepTask': self._ceptask,
            'GlobalTrend': self._global_trend,
            'IntelligentAnalysis': self._intelligent_analysis,
            'Dashboard': self._dashboard,
            'Component': self._component,
            'ComponentGroup': self._component_group,
            'ReportTemplate': self._report_template,
            'AssetView': self._asset_view,
            'TimeReport': self._time_report,
            'Role': self._role,
            'AuditLog': self._auditlog,
            'Vulnerability': self._vulnerability,
            'DVCollector': self._dvcollector,
            'DVParser': self._dvparser,
            'DVSource': self._dvsource,
            'AssetBusiness': self._asset_business,
            'AssetDomain': self._asset_domain,
            'AssetLocation': self._asset_location,
            'InitConfig': self._init_config,

        }.get(resource, None)

    def module_exec(self, module, func, **kwargs):
        resource = self.get_resource(module)
        if resource:
            return getattr(resource, func)(**kwargs)
