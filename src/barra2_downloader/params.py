try:
    from .model_domains import BARRAFrequency, BARRADomain, BARRAModel, BARRAVarClass, BARRAModelDomainFrequency, BARRAVariableInfo
except:
    from model_domains import BARRAFrequency, BARRADomain, BARRAModel, BARRAVarClass, BARRAModelDomainFrequency, BARRAVariableInfo
import json
from importlib import resources

# The file which contains the variable definitions
_VARIABLE_FNAME = 'barra_variables.json'

# Load in the BARRA variable list
BARRA_VARS = {}

try:
    raw_var_list = json.load(
        resources.files('barra2_downloader').joinpath(_VARIABLE_FNAME).open('r')
    )
except:
    raw_var_list = json.load(open("./src/barra2_downloader/barra_variables.json", 'r'))

for var_name in raw_var_list:
    var_data = raw_var_list[var_name]
    var_class = BARRAVarClass(var_data['class'].split("/")[-1]) # TODO: Make it accept multiple classes, currently just uses the last one (lowest)
    mdfs = []
    for s in var_data['mdf']:
        try:
            s = s.split("/")
            model = BARRAModel(s[0])
            domain = BARRADomain(s[1])
            frequency = BARRAFrequency(s[2])
            mdfs.append((model, domain, frequency))
        except:
            pass
    BARRA_VARS[var_name] = (var_data['name'], var_data['desc'], mdfs, var_class, var_data['comment'])

def check_valid_pairing(
        var: str,
        mdf: BARRAModelDomainFrequency
    ):
    return (var in BARRA_VARS) and (mdf in BARRA_VARS[var][2]) # It is in the list and it's available in the given model/domain/frequency

def get_available_parameters(
        model: BARRAModel,
        domain: BARRADomain,
        frequency: BARRAFrequency    
    ):

    mdf = (model, domain, frequency)
    vars = []
    for var in BARRA_VARS:
        if mdf in BARRA_VARS[var][2]:
            vars.append(var)
    return vars