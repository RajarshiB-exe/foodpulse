from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor

ORDER_VALUE = "subtotal + tax + delivery_fee - discount"
CONTRIBUTION = "platform_fee + delivery_fee - delivery_cost - payment_cost"

def _orders(s):
    rows=s.execute(text(f"select id, restaurant_id, date, {ORDER_VALUE} value, {CONTRIBUTION} contribution, discount from orders order by date")).mappings().all()
    return pd.DataFrame(rows)

def dashboard(s):
    df=_orders(s)
    gmv=float(df.value.sum()); orders=len(df); aov=gmv/orders if orders else 0
    discounts=float(df.discount.sum()); contribution=float(df.contribution.sum())
    daily=df.groupby('date', as_index=False).agg(gmv=('value','sum'), contribution=('contribution','sum'), orders=('id','count'))
    daily['date']=daily.date.astype(str); daily=daily[['date','gmv','contribution','orders']]
    cuisines=s.execute(text("select cuisine,count(*) restaurants from restaurants group by cuisine order by restaurants desc")).mappings().all()
    areas=s.execute(text("select area,count(*) restaurants from restaurants group by area order by restaurants desc")).mappings().all()
    return {"gmv":gmv,"orders":orders,"aov":aov,"discount_rate":discounts/gmv if gmv else 0,"contribution":contribution,"contribution_margin":contribution/gmv if gmv else 0,"daily":daily.to_dict('records'),"cuisines":[dict(x) for x in cuisines],"areas":[dict(x) for x in areas]}

def anomalies(s):
    df=_orders(s)
    if df.empty: return []
    g=df.groupby('restaurant_id').agg(orders=('id','count'),gmv=('value','sum'),discounts=('discount','sum'),contribution=('contribution','sum')).reset_index()
    features=g[['orders','gmv','discounts','contribution']].fillna(0)
    if len(g)<5: return []
    model=IsolationForest(contamination=0.15, random_state=42).fit(features)
    g['anomaly_score']=model.decision_function(features); g['is_anomaly']=model.predict(features)==-1
    names={r['id']:r['name'] for r in s.execute(text('select id,name from restaurants')).mappings().all()}
    out=g[g.is_anomaly].sort_values('anomaly_score').head(8)
    return [{"restaurant_id":int(r.restaurant_id),"restaurant":names.get(int(r.restaurant_id),"Unknown"),"orders":int(r.orders),"gmv":float(r.gmv),"contribution":float(r.contribution),"score":round(float(r.anomaly_score),3)} for _,r in out.iterrows()]

def forecast(s):
    df=_orders(s)
    daily=df.groupby('date').agg(gmv=('value','sum'),orders=('id','count')).reset_index()
    daily['t']=np.arange(len(daily));
    if len(daily)<14: return []
    model=RandomForestRegressor(n_estimators=150,random_state=42,min_samples_leaf=2).fit(daily[['t']],daily['gmv'])
    future=np.arange(len(daily),len(daily)+14)
    dates=pd.date_range(pd.to_datetime(daily.date.max())+pd.Timedelta(days=1),periods=14)
    preds=model.predict(future.reshape(-1,1))
    return [{"date":d.strftime('%Y-%m-%d'),"gmv":round(float(p),2)} for d,p in zip(dates,preds)]

def restaurant_economics(s, rid):
    exists=s.execute(text('select id,name,area,cuisine,rating,reviews,cost_for_two from restaurants where id=:r'),{'r':rid}).mappings().first()
    if not exists: return None
    r=s.execute(text(f"select count(*) orders,coalesce(sum({ORDER_VALUE}),0) gmv,coalesce(avg({ORDER_VALUE}),0) aov,coalesce(sum(discount),0) discounts,coalesce(sum({CONTRIBUTION}),0) contribution from orders where restaurant_id=:r"),{'r':rid}).mappings().one()
    x=dict(exists); x.update(dict(r)); x['margin_pct']=float(r['contribution']/r['gmv']*100) if r['gmv'] else 0; return x

def menu_economics(s, rid):
    rows=s.execute(text("""
    select m.id,m.name,m.category,m.price,count(oi.id) units,coalesce(sum(oi.quantity*m.price),0) gross_sales
    from menu_items m left join order_items oi on oi.menu_item_id=m.id
    where m.restaurant_id=:r group by m.id order by units desc, gross_sales desc
    """),{'r':rid}).mappings().all()
    return [dict(x) for x in rows]

def review_intelligence(s):
    rows=s.execute(text('select rating,text as comment from reviews order by id desc limit 500')).mappings().all()
    pos=['great','excellent','fast','tasty','delicious','good','fresh','amazing','love','quick']
    neg=['late','cold','bad','poor','slow','missing','wrong','rude','overpriced','worst']
    topics={'delivery':['late','slow','delivery','rider'],'food':['tasty','delicious','cold','fresh','taste'],'price':['expensive','overpriced','price','value'],'service':['rude','support','missing','wrong']}
    counts={'positive':0,'neutral':0,'negative':0}; topic_counts={k:0 for k in topics}
    for r in rows:
        t=(r['comment'] or '').lower(); score=sum(w in t for w in pos)-sum(w in t for w in neg)
        label='positive' if score>0 else 'negative' if score<0 else 'neutral'; counts[label]+=1
        for k,words in topics.items(): topic_counts[k]+=sum(w in t for w in words)
    return {'reviews_analyzed':len(rows),'sentiment':counts,'topics':sorted([{'topic':k,'mentions':v} for k,v in topic_counts.items()],key=lambda x:x['mentions'],reverse=True)}
