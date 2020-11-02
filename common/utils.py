from dtsa import config

def get_parameter(parameter_list, parameters):
    parameter_dict = dict()
    for p in parameter_list:
        if p in parameters:
            parameter_dict[p] = parameters[p]

    return parameter_dict
