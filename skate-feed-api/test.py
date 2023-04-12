import json

def getJsonData():
    try:
        with open("./skate-feed-api/source_data.json", "r") as j:
            contents = json.loads(j.read())
            print(contents)
            # for key, value in test.items():
            #     print(key, value)
            # for i in test:
            #     print(test[i])
    except ValueError as e:
        print('json fail')
        print(e)


if __name__ == '__main__':
    getJsonData()