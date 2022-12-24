import collections
from os import path

import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import  json

# conn = psycopg2.connect("dbname=products user=donat password=123")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewProduct(BaseModel):
    # id: int
    name: str
    description: str
    price: float
    imgURL: str

class EditProduct(BaseModel):
    id: int
    name: str
    description: str
    price: float
    imgURL: str

# def writeToJSONFile(path, fileName, data):
#     filePathNameWExt = './' + path + '/' + fileName + '.json'
#     with open(filePathNameWExt, 'w') as fp:
#         json.dump(data, fp)

# def addToJSONFile(filename, data: NewProduct):
#     # Check if file exists
#     if path.isfile(filename) is False:
#         raise Exception("File not found")
#
#     # Read JSON file
#     with open(filename) as fp:
#         listObj = json.load(fp)
#
#     # Verify existing list
#     print(listObj)
#     print(type(listObj))
#
#     listObj.append({
#         "id": len(listObj),
#         "productName": "Person_3",
#         "productPrice": 33,
#         "productDescription": data[],
#         "imgURL": data['imgURL']
#     })
#
#     # Verify updated list
#     print(listObj)
#
#     with open(filename, 'w') as json_file:
#         json.dump(listObj, json_file,
#                   indent=4,
#                   separators=(',', ': '))
#
#     print('Successfully appended to the JSON file')

file_name = "products1"

def get_in_json(result):
    return json.dumps([dict(ix) for ix in result])

@app.get("/")
async def read_item():
    # with open("products.json", "r") as file:
    #     jsonProducts = json.load(file)
    # file.close()
    # return jsonProducts
    conn = psycopg2.connect(user="donat",
                            password="123",
                            host="127.0.0.1",
                            port="5432",
                            database="myshop")
    cursor = conn.cursor()
    cursor.execute('''SELECT * from products''')

    rows = cursor.fetchall()
    # result = get_in_json(result)
    # print(result)
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['productName'] = row[1]
        d['productPrice'] = row[2]
        d['productDescription'] = row[3]
        d['imgURL'] = row[4]
        objects_list.append(d)

    print(json.dumps(objects_list))
    with open("products1.json", 'w') as json_file:
        json.dump(objects_list, json_file,
                      indent=2,
                      separators=(',', ': '))
        json_file.close()

    conn.close()

    with open("products1.json", "r") as file:
        jsonProducts = json.load(file)
    file.close()
    return jsonProducts
    # return json.dumps(objects_list)

@app.post("/admin/product/add")
async def add_product(product: NewProduct):
    try:
        conn = psycopg2.connect(user="donat",
                                password="123",
                                host="127.0.0.1",
                                port="5432",
                                database="myshop")
        cursor = conn.cursor()
        postgres_insert_query = """ INSERT INTO products(product_name, product_price, product_description, image_url) 
                                    VALUES (%s,%s,%s,%s)"""
        data_to_insert = (product.name, product.price, product.description, product.imgURL)
        cursor.execute(postgres_insert_query, data_to_insert)

        conn.commit()
        count = cursor.rowcount
        print(count, "Product inserted successfully into table")
        return {"status": 200}

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert into table", error)

    finally:
        # closing database connection.
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

@app.put("/admin/product/edit")
async def edit_product(product: EditProduct):
    try:
        conn = psycopg2.connect(user="donat",
                                password="123",
                                host="127.0.0.1",
                                port="5432",
                                database="myshop")
        cursor = conn.cursor()

        print("Table Before updating record ")
        sql_select_query = """select * from products where product_id = %s"""
        cursor.execute(sql_select_query, (product.id,))
        record = cursor.fetchone()
        print(record)

        # Update single record now
        sql_update_query = """  Update products 
                                set product_name = %s,
                                    product_price = %s,
                                    product_description = %s,
                                    image_url = %s
                                where product_id = %s"""
        cursor.execute(sql_update_query, (product.name, product.price, product.description,
                                          product.imgURL, product.id))
        conn.commit()
        count = cursor.rowcount
        print(count, "Product updated successfully")

        print("Table After updating record ")
        sql_select_query = """select * from products where product_id = %s"""
        cursor.execute(sql_select_query, (product.id,))
        record = cursor.fetchone()
        print(record)
        return {"status": 200}

    except (Exception, psycopg2.Error) as error:
        print("Failed to update product in table", error)

    finally:
        # closing database connection.
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

class DeleteProduct(BaseModel):
    id: int

@app.delete("/admin/product/delete")
async def delete_product(product: DeleteProduct):
    try:
        conn = psycopg2.connect(user="donat",
                                password="123",
                                host="127.0.0.1",
                                port="5432",
                                database="myshop")
        cursor = conn.cursor()
        sql_delete_query = """Delete from products where product_id = %s"""
        cursor.execute(sql_delete_query, (product.id,))
        conn.commit()
        count = cursor.rowcount
        print(count, "Product deleted successfully")
        return {"status": 200}

    except (Exception, psycopg2.Error) as error:
        print("Failed to delete product in the table", error)

    finally:
        # closing database connection.
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

