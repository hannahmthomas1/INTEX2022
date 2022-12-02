from .models import FoodItem

def searchAPI(queryValue):
    import requests
    nutrients = ['Protein', 'Sodium, Na', 'Potassium, K', 'Water', 'Phosphorus, P']
    foodInfo = []
    r = requests.get(f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key=ZG2gfG4lRbZh0UXSFos1GvXbvUrvjsdYX7kYBdVI&query={queryValue}&pageSize=5')
    for i in r.json()['foods']:
        nuts = {}
        name = i['description'].lower()
        id = i['fdcId']
        for j in i['foodNutrients']:
            if j['nutrientName'] in nutrients:
                nuts[j['nutrientName']] = j['value']
        foodInfo.append({
            'id':id,
            'name':name,
            'nutrients': nuts
        })
    return foodInfo

def getById(id):
    import requests
    data = {}
    nutrients = ['Protein', 'Sodium, Na', 'Potassium, K', 'Water', 'Phosphorus, P']
    r = requests.get(f'https://api.nal.usda.gov/fdc/v1/food/{id}?api_key=ZG2gfG4lRbZh0UXSFos1GvXbvUrvjsdYX7kYBdVI')
    jason = r.json()
    data['name'] = jason['description'].lower()
    data['unit'] = jason['servingSizeUnit']
    data['serving_size'] = jason['servingSize']
    for i in jason['foodNutrients']:
        if i['nutrient']['name'] in nutrients:
            data[i['nutrient']['name']] = i['amount']
    return data


def getList(num): #pulls records from api and stores in postgres
    import requests
    data = []
    fin = []
    nutrients = ['Protein', 'Sodium, Na', 'Potassium, K', 'Water', 'Phosphorus, P']
    #dataType = [ "Foundation" ]
    params = {
        'pageSize': num,
        'sortBy':'fdcId',
    }
    # for index in range(0, len(dataType)):
    #     field = dataType[index]
    #     params[f"outputSelector[{index}]"] = field
    r = requests.get('https://api.nal.usda.gov/fdc/v1/foods/list?api_key=ZG2gfG4lRbZh0UXSFos1GvXbvUrvjsdYX7kYBdVI', params)
    res = r.json()
    for i in res:
        food = {
            'name' : i['description'].lower(),
            'fdic' : i['fdcId'],
        }
        for j in i['foodNutrients']:
            if j['name'] in nutrients:
                food[j['name']] = j['amount']
        fin.append(food)
        for i in fin:
            if i not in data:
                data.append(i)
        for record in data:
            item = FoodItem()
            item.fdic = record['fdic']
            item.FoodName = record['name']
            if 'Sodium, Na' in record:
                item.Sodium_mg = record['Sodium, Na']
            else:
                item.Sodium_mg = 0
            if 'Protein' in record:
                item.Protein_g = record['Protein']
            else:
                item.Protein_g = 0
            if 'Potassium, K' in record:
                item.Potassium_mg = record['Potassium, K']
            else:
                item.Potassium_mg = 0
            if 'Phosphorus, P' in record:
                item.Phosphate_mg = record['Phosphorus, P']
            else:
                item.Phosphate_mg = 0
            if 'Water' in record:
                item.Water_L = record['Water']
            else:
                item.Water_L = 0
            item.save()
    return data

    



