from fastapi import FastAPI,Request,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine,Column,Integer,String,Float
from sqlalchemy.orm import sessionmaker,declarative_base
from fastapi.staticfiles import StaticFiles
#creating an engine and making sessions
url="mysql+mysqlconnector://root:Pavani%40123@localhost:3306/Products"
engine=create_engine(url)
LocalSession=sessionmaker(bind=engine,autoflush=True)
template=Jinja2Templates(directory="productfiles")
app=FastAPI()
Base=declarative_base()
class product(BaseModel):
    productname:str
    productprice:int
    productdesc:str
app.mount("/static",StaticFiles(directory="productfiles"),name="static")
#Creating a tables class for products
class Products(Base):
    __tablename__="ProductsData"
    product_id=Column(Integer,primary_key=True,autoincrement=True,index=True)
    product_name=Column(String(20),nullable=False)
    product_price=Column(Float,nullable=False)
    product_description=Column(String(200),nullable=False)
Base.metadata.create_all(bind=engine)
def display():
    db=LocalSession()
    products=db.query(Products).all()
    return products
@app.get('/',response_class=HTMLResponse)
def home(req:Request):
    return template.TemplateResponse(request=req,name="home.html")
@app.get("/product_info",response_class=HTMLResponse)
def showproducts(req:Request):
    products=display()
    return template.TemplateResponse(request=req,name="product_info.html",context={"products":products
    })
@app.get("/add", response_class=HTMLResponse)
def add_page(req:Request):
    return template.TemplateResponse(request=req,name="add.html")
@app.post("/addproduct",response_class=HTMLResponse)
def addproduct(req:Request,productname: str = Form(),productprice:int= Form(), productdesc:str=Form()):
    db=LocalSession()
    if productname and productprice and productdesc:
        pro=Products(product_name=productname,product_price=productprice,product_description=productdesc)
    if pro:
        db.add(pro)
        db.commit()
        db.close()
    else:
        return "Enter Valid Product Data"
    product_list=display()
    return template.TemplateResponse(request=req,name="product_info.html",
                                     context={"products":product_list})

@app.get("/delete-page", response_class=HTMLResponse)
def delete_page(req:Request):
    return template.TemplateResponse(request=req,name="delete.html")
@app.post('/deleteproduct',response_class=HTMLResponse)
def deleteproduct(req:Request,id:int=Form()):
    db=LocalSession()
    try:
        product=db.query(Products).filter(Products.product_id==id).first()
        if product:
            db.delete(product)
            db.commit()
        else:
            product_list=db.query(Products).all()
            return template.TemplateResponse(request=req,
                                         name="product_info.html",
                                         context={
                                             "products":product_list,
                                             "message":"Enter product with valid ID"
                                         })
        product_list=db.query(Products).all()
        return template.TemplateResponse(request=req,
                                                 name="product_info.html",
                                                 context={
                                                     "products":product_list
                                                 })
    finally:
        db.close()