from enum import Enum
from typing import TypeAlias

class BARRAModel(Enum):
    BARRA_C2 = "BARRA-C2"
    BARRA_R2 = "BARRA-R2"
    BARRA_RE2 = "BARRA-RE2"

class BARRADomain(Enum):
    AUST_04 = "AUST-04"
    AUST_11 = "AUST-11"
    AUS_11 = "AUS-11"
    AUS_22 = "AUS-22"

class BARRAVarClass(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class BARRAFrequency(Enum):
    min20 = "20min"
    hour = "1hr"
    day = "day"
    month = "mon"
    fx = "fx"
    hour_3 = "3hr"

BARRAModelDomainFrequency: TypeAlias = tuple[BARRAModel, BARRADomain, BARRAFrequency]
BARRAVariableInfo: TypeAlias = tuple[str, str, list[BARRAModelDomainFrequency], BARRAVarClass, str] # long name, description, list of model/domain/frequency available in, variable class, comment