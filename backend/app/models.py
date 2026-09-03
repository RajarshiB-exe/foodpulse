from sqlalchemy import String, Integer, Float, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base
class Restaurant(Base):
    __tablename__="restaurants"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(120),index=True)
    area:Mapped[str]=mapped_column(String(80),index=True)
    cuisine:Mapped[str]=mapped_column(String(80),index=True)
    rating:Mapped[float]=mapped_column(Float,default=4.0)
    reviews:Mapped[int]=mapped_column(Integer,default=0)
    cost_for_two:Mapped[float]=mapped_column(Float,default=400)
class MenuItem(Base):
    __tablename__="menu_items"
    id:Mapped[int]=mapped_column(primary_key=True)
    restaurant_id:Mapped[int]=mapped_column(ForeignKey("restaurants.id"))
    name:Mapped[str]=mapped_column(String(160))
    category:Mapped[str]=mapped_column(String(80))
    price:Mapped[float]=mapped_column(Float)
    cost:Mapped[float]=mapped_column(Float)
    popularity:Mapped[float]=mapped_column(Float,default=50)
class Order(Base):
    __tablename__="orders"
    id:Mapped[int]=mapped_column(primary_key=True)
    restaurant_id:Mapped[int]=mapped_column(ForeignKey("restaurants.id"))
    date:Mapped[object]=mapped_column(Date)
    subtotal:Mapped[float]=mapped_column(Float)
    discount:Mapped[float]=mapped_column(Float,default=0)
    delivery_fee:Mapped[float]=mapped_column(Float,default=0)
    tax:Mapped[float]=mapped_column(Float,default=0)
    platform_fee:Mapped[float]=mapped_column(Float,default=0)
    delivery_cost:Mapped[float]=mapped_column(Float,default=0)
    payment_cost:Mapped[float]=mapped_column(Float,default=8)
class Review(Base):
    __tablename__="reviews"
    id:Mapped[int]=mapped_column(primary_key=True)
    restaurant_id:Mapped[int]=mapped_column(ForeignKey("restaurants.id"))
    date:Mapped[object]=mapped_column(Date)
    text:Mapped[str]=mapped_column(Text)
    rating:Mapped[float]=mapped_column(Float)
    sentiment:Mapped[float]=mapped_column(Float,default=0)

class OrderItem(Base):
    __tablename__="order_items"
    id:Mapped[int]=mapped_column(primary_key=True)
    order_id:Mapped[int]=mapped_column(ForeignKey("orders.id"))
    menu_item_id:Mapped[int]=mapped_column(ForeignKey("menu_items.id"))
    quantity:Mapped[int]=mapped_column(Integer,default=1)
