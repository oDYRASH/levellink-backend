def transform_region(region):
    if region in ["eun1", "euw1", "tr1", "ru"]:
        return "europe"
    elif region in ["kr", "jp1"]:
        return "asia"
    elif region in ["na1", "la1", "la2", "br1", "oc1"]:
        return "americas"
    else:
        return "europe"
