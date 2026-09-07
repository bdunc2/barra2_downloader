from model_domains import BARRAFrequency, BARRADomain, BARRAModel, BARRAVarClass, BARRAModelDomainFrequency, BARRAVariableInfo
import json

# The file which contains the variable definitions
_VARIABLE_FNAME = "./src/barra2_downloader/barra_variables.json"

# Load in the BARRA variable list
BARRA_VARS = {}
raw_var_list = json.load(open(_VARIABLE_FNAME, 'r'))
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