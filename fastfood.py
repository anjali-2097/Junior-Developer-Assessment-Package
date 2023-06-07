import pandas as pd
import mysql.connector as msql
from mysql.connector import Error
import matplotlib.pyplot as plt
import numpy as np
import re

def create_database():
    try:
        conn = msql.connect(host='localhost', user='root', password='')  # provide your username and password
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE fastfood")
            print("Database created successfully")
    except Error as e:
        print("Error while connecting to MySQL", e)


def create_connection():
    try:
        conn = msql.connect(host='localhost', database='fastfood', user='root', password='')  # provide your username and password
        if conn.is_connected():
            print("Connected to the database")
            return conn
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None


def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS fastfood")
        cursor.execute("CREATE TABLE fastfood(id int AUTO_INCREMENT primary key NOT NULL,restaurant varchar(255),item varchar(255),calories int,cal_fat int,total_fat int,sat_fat float(13,2),trans_fat float(13,2),cholesterol int,sodium int,total_carb int,fiber int, sugar int, protein int, vit_a int, vit_c int, calcium int, salad varchar(255))")
        print("Table created successfully")
    except Error as e:
        print("Error while creating the table", e)


def insert_data_from_csv(conn, data):
    try:
        cursor = conn.cursor()
        for i, row in data.iterrows():
            cursor.execute("INSERT INTO fastfood.fastfood VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (i + 1, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16]))
        conn.commit()
        print("Data inserted successfully")
    except Error as e:
        print("Error while inserting data into the table", e)


def visualize_top_restaurants(conn):
    try:
        cursor = conn.cursor()
        sql = "SELECT restaurant, Min(calories) as minimum_calories,Max(calories) as maximum_calories,Avg(calories) as average_calories, Avg(total_carb) as average_carbs FROM fastfood GROUP BY restaurant ORDER BY Avg(total_carb) ASC LIMIT 5"
        cursor.execute(sql)
        records = cursor.fetchall()

        restaurants = []
        minimum_calories = []
        maximum_calories = []
        average_calories = []
        average_carbs = []

        for row in records:
            restaurants.append(row[0])
            minimum_calories.append(row[1])
            maximum_calories.append(row[2])
            average_calories.append(row[3])
            average_carbs.append(row[4])

        print("Top 5 restaurants are:", restaurants)
        nutrient = {
            "Minimum Calories": tuple(minimum_calories),
            "Maximum Calories": tuple(maximum_calories),
            "Average Calories": tuple(average_calories),
            "Average Carbs": tuple(average_carbs)
        }

        x = np.arange(len(restaurants))
        width = 0.20
        multiplier = 0

        fig, ax = plt.subplots(figsize=(15, 11))
        for attribute, measurement in nutrient.items():
            offset = width * multiplier
            rects = ax.bar(x + offset, measurement, width, label=attribute)
            ax.bar_label(rects, padding=3)
            multiplier += 1

        ax.set_ylabel('Average Carbs')
        ax.set_title('Top 5 Restaurants with Least Average Carbs')
        ax.set_xticks(x + width, restaurants)
        ax.legend(loc='upper left', ncols=4)
        ax.set_ylim(0, 1700)

        plt.show()
    except Error as e:
        print("Error while visualizing data", e)


def categorize_items(conn):
    categories = {}
    categorized_items = []

    try:
        cursor = conn.cursor()
        sql = "SELECT restaurant, item FROM fastfood"
        cursor.execute(sql)
        records = cursor.fetchall()

        for row in records:
            if re.search('small|salad|fries|rice|soup|nacho|strips|cheese curds|dip|bowl|doritos|potato|Quesadilla|Mushrooms|Chickstar', row[1], re.IGNORECASE):
                category = "Side"
                sub_category = "NA"
            elif re.search('large|big|taco|burger|double|chicken|fish|Rib|beef|BLT|tenders|gyro|bacon|ham|sub|sandwich|tostada|turkey|pizza|footlong|6|steak|roll|wrap|dog|burrito|king|Quarter|Slider|Deluxe|Melt|Stacker|WHOPPER|Brisket|Gordita', row[1], re.IGNORECASE):
                category = "Main"
                if re.search('Chicken', row[1], re.IGNORECASE):
                    sub_category = "Chicken"
                elif re.search('Beef', row[1], re.IGNORECASE):
                    sub_category = "Beef"
                elif re.search('Pork', row[1], re.IGNORECASE):
                    sub_category = "Pork"
                elif re.search('Seafood|fish|Crab|Lobster|Shrimp|Salmon', row[1], re.IGNORECASE):
                    sub_category = "Seafood"
                else:
                    sub_category = "Other"
            else:
                category = "Dessert"
                sub_category = "NA"

            categories[row[1]] = category, sub_category
            categorized_items.append((row[0], row[1], category, sub_category))

        categorized_data = pd.DataFrame(categorized_items, columns=['Restaurant', 'Item', 'Category', 'Sub Category'])
        categorized_data.to_csv('foodcats.csv', index=False)
        print("Data categorized and saved as foodcats.csv")
    except Error as e:
        print("Error while categorizing data", e)


# Read data from CSV and replace NaN values with 0
fooddata = pd.read_csv('fastfood.csv', index_col=False, delimiter=',')
fooddata = fooddata.fillna(0)

# Create database
create_database()

# Connect to the database
conn = create_connection()

if conn:
    # Create table in the database
    create_table(conn)

    # Insert data from CSV into the database
    insert_data_from_csv(conn, fooddata)

    # Visualize top restaurants
    visualize_top_restaurants(conn)

    # Categorize items and save the result in CSV file
    categorize_items(conn)

    # Close the database connection
    conn.close()
else:
    print("Unable to connect to the database")