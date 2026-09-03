from datetime import date, timedelta
from sqlalchemy.orm import Session
from .models import Restaurant, MenuItem, Order, Review, OrderItem
import random

random.seed(42)

RESTAURANTS = [
    ("Bengal Table", "Park Street", "Bengali", 4.4, 2840, 700),
    ("Calcutta Social Kitchen", "Ballygunge", "Bengali", 4.3, 1930, 650),
    ("Salt Lake Biryani Co.", "Salt Lake", "Biryani", 4.2, 3410, 520),
    ("Royal Dum Kitchen", "New Town", "Biryani", 4.5, 4120, 580),
    ("Eastern Wok", "Park Street", "Chinese", 4.1, 1680, 620),
    ("Lotus Bowl", "Salt Lake", "Chinese", 4.3, 2210, 560),
    ("The Pizza Room", "Ballygunge", "Pizza", 4.2, 3050, 720),
    ("Crust & Co.", "New Town", "Pizza", 4.4, 2670, 680),
    ("Madras House", "Garia", "South Indian", 4.3, 1840, 420),
    ("Coconut Leaf", "Salt Lake", "South Indian", 4.5, 2360, 460),
    ("Grill District", "New Town", "Burgers", 4.1, 1520, 500),
    ("Stacked Burger Co.", "Park Street", "Burgers", 4.2, 1980, 540),
    ("The Bengal Kitchen", "Behala", "Bengali", 4.0, 1290, 480),
    ("Home Plate Kolkata", "Garia", "Bengali", 4.2, 1570, 450),
    ("Dum & Spice", "Behala", "Biryani", 4.1, 1760, 490),
    ("Biryani Works", "Garia", "Biryani", 4.4, 2510, 510),
    ("Wok Street", "New Town", "Chinese", 4.0, 1430, 550),
    ("Golden Chopsticks", "Ballygunge", "Chinese", 4.2, 1890, 590),
    ("Napoli Kitchen", "Park Street", "Pizza", 4.3, 2130, 690),
    ("Oven & Olive", "Salt Lake", "Pizza", 4.1, 1740, 630),
    ("Udupi Central", "Garia", "South Indian", 4.2, 2020, 400),
    ("Southern Spoon", "Behala", "South Indian", 4.4, 1650, 430),
    ("Burger Yard", "Ballygunge", "Burgers", 4.0, 1380, 520),
    ("Urban Grill House", "New Town", "Burgers", 4.3, 2260, 570),
]

MENU_TEMPLATES = {
    "Bengali": [("Kosha Mangsho", 390), ("Bhetki Paturi", 360), ("Luchi & Alur Dom", 220), ("Basanti Pulao", 260), ("Fish Curry Rice", 310), ("Mishti Doi", 120)],
    "Biryani": [("Chicken Biryani", 280), ("Mutton Biryani", 360), ("Egg Biryani", 220), ("Chicken Chaap", 320), ("Mutton Chaap", 390), ("Raita", 90)],
    "Chinese": [("Chilli Chicken", 330), ("Hakka Noodles", 260), ("Fried Rice", 240), ("Kung Pao Chicken", 360), ("Veg Manchurian", 250), ("Spring Rolls", 190)],
    "Pizza": [("Margherita", 360), ("Farmhouse", 460), ("Chicken Tikka Pizza", 520), ("Four Cheese", 540), ("Pepperoni", 560), ("Garlic Bread", 220)],
    "South Indian": [("Masala Dosa", 190), ("Idli Sambar", 150), ("Ghee Roast Dosa", 230), ("Vada Sambar", 160), ("South Indian Meals", 280), ("Filter Coffee", 110)],
    "Burgers": [("Classic Chicken Burger", 280), ("Crispy Chicken Burger", 320), ("Veggie Burger", 240), ("Double Smash Burger", 390), ("Loaded Fries", 210), ("Chicken Wings", 300)],
}

REVIEW_TEXT = [
    ("Food was fresh and well packed. Delivery was quick.", 5),
    ("Good portion and tasty food. Would order again.", 4),
    ("Food arrived cold and delivery was late.", 2),
    ("The taste was good but the price felt high.", 3),
    ("Excellent packaging and fast delivery.", 5),
    ("Portion was smaller than expected for the price.", 3),
]

def seed(db: Session):
    if db.query(Restaurant).count():
        return

    restaurants = []
    for name, area, cuisine, rating, reviews, cost_for_two in RESTAURANTS:
        r = Restaurant(name=name, area=area, cuisine=cuisine, rating=rating, reviews=reviews, cost_for_two=cost_for_two)
        db.add(r)
        restaurants.append(r)
    db.flush()

    for r in restaurants:
        for item_name, price in MENU_TEMPLATES[r.cuisine]:
            cost = round(price * random.uniform(0.30, 0.47), 2)
            db.add(MenuItem(restaurant_id=r.id, name=item_name, category=r.cuisine, price=price, cost=cost, popularity=random.uniform(35, 96)))
    db.flush()

    start = date.today() - timedelta(days=89)
    for day_index in range(90):
        dt = start + timedelta(days=day_index)
        weekend = dt.weekday() >= 5
        for r in restaurants:
            base = random.randint(10, 24) + (random.randint(4, 10) if weekend else 0)
            for _ in range(base):
                subtotal = random.randint(260, 820)
                discount = random.choice([0, 0, 20, 30, 40, 50, 70])
                delivery_fee = random.randint(20, 55)
                tax = round(subtotal * 0.05, 2)
                platform_fee = round(subtotal * random.uniform(0.17, 0.23), 2)
                delivery_cost = round(random.uniform(22, 52), 2)
                payment_cost = round(max(5, subtotal * 0.015), 2)
                order = Order(restaurant_id=r.id, date=dt, subtotal=subtotal, discount=discount, delivery_fee=delivery_fee, tax=tax, platform_fee=platform_fee, delivery_cost=delivery_cost, payment_cost=payment_cost)
                db.add(order)
                db.flush()
                item_id = (r.id - 1) * 6 + random.randint(1, 6)
                db.add(OrderItem(order_id=order.id, menu_item_id=item_id, quantity=random.randint(1, 2)))

    for r in restaurants:
        for _ in range(16):
            text, rating = random.choice(REVIEW_TEXT)
            db.add(Review(restaurant_id=r.id, date=start + timedelta(days=random.randint(0, 89)), text=text, rating=rating, sentiment=(rating - 3) / 2))

    db.commit()
