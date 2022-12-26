from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import requests
import lxml
from fuzzywuzzy import fuzz
from .models import Product
def generateURL(product_name,url_1,url_2):
  return url_1+product_name+url_2
def home(request):
    return render(request,"index.html")
def get(request):
  
  headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
  
  product = request.GET["product"]

  print(product)
  amazon_url_1="https://www.amazon.in/s?k="
  amazon_url_2="&crid=30H5OAIPN2OL9&sprefix=%2Caps%2C233&ref=nb_sb_ss_recent_1_0_recent"

  url=generateURL(product,amazon_url_1,amazon_url_2)
  page=requests.get(url,headers=headers)
  data=BeautifulSoup(page.text,"lxml")
  data.prettify()
  final=data.find_all(class_="s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")

 
  title=data.find_all(class_=["a-size-medium a-color-base a-text-normal"])
  price=data.find_all(class_="a-price-whole")
  image_link=data.find_all(class_="s-image")
  product_link = data.find_all(class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
  products_list = []
  count=min(len(title),len(price),len(image_link))

  amazon_product_list=[]
  for i in range(count):
    item = Product()
    
    item.title=title[i].text
    
    
    item.price=price[i].text
    try:
      item.link="http://amazon.in"+product_link[i]['href']
    except:
      continue
    try:
      item.image=image_link[i]["src"]
    except:
      continue
    amazon_product_list.append(item)

  flipkart_url1='https://www.flipkart.com/search?q='
  flipkart_url2='&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off'

  product_url=flipkart_url1+product+flipkart_url2
  page=requests.get(product_url,headers=headers)
  data=BeautifulSoup(page.text,'lxml')
  data.prettify()

  products_list=[]

  title=data.find_all(class_="_4rR01T")

  image_link=data.find_all(class_="_396cs4")

  price=data.find_all(class_="_30jeq3 _1_WHN1")

  product_link = data.find_all(class_="_1fQZEK")

  if(len(title)==0):

    title=data.find_all(class_="s1Q9rs")
    image_link=data.find_all(class_="_396cs4")
    price=data.find_all(class_="_30jeq3")
    product_link = data.find_all(class_="_2rpwqI")
  if len(title) == 0:
    title=data.find_all(class_="IRpwTa")
    image_link=data.find_all(class_="_2r_T1I")
    price=data.find_all(class_="_30jeq3")
    product_link = data.find_all(class_="_3bPFwb")

  flipkart_product_list = []
  x=min(len(title),len(image_link),len(price),len(product_link))
  for i in range(1,x):
    item = Product()

    item.title=title[i].text
    
  

    item.image=image_link[i]["src"]
    item.price=price[i].text
    item.link="http://flipkart.com"+product_link[i]['href']
    flipkart_product_list.append(item)

  amazonProduct = amazon_product_list[0]
  flipkartProduct = flipkart_product_list[0]
  accuracy = fuzz.ratio(product,amazonProduct.title)

  for item1 in amazon_product_list:
    temp=fuzz.ratio(product,item1.title)
    if accuracy<temp:
      accuracy=temp
      amazonProduct = item1
  accuracy = fuzz.ratio(product,flipkartProduct.title)
  for item1 in flipkart_product_list:
    temp=fuzz.ratio(product,item1.title)
    if accuracy<temp:
      accuracy=temp
      flipkartProduct = item1
  return render(request,"result.html",{"flipkart":flipkartProduct,"amazon":amazonProduct})

  