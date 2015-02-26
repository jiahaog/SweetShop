from flask import render_template, request, redirect, url_for
from app import app
import urllib
import urllib2

# ROOT_URL = 'http://127.0.0.1:5000'
ROOT_URL = 'https://sweetshop.herokuapp.com'


USER = 'jh-seller_api1.gmail.com'
PWD = 'STEQUJHBE7G8YE6C'
SIGNATURE = 'ABJn0t6lSvhISGgOOG5rpe-BZf42A8MSNs5HNoOzQQzlRWj3jk52NRvy'
API_SERVER = 'https://api-3t.sandbox.paypal.com/nvp'

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'John'}

    return render_template('index.html',
                            user=user)



@app.route('/buy')
def buy():
    print "buying"  

    returnUrl = ROOT_URL  + '/getCheckoutDetails'
    cancelUrl = ROOT_URL + '/cancel'
    
    values = {

        'METHOD' : 'SetExpressCheckout',
        'VERSION' : '109.0',
        
        'USER' : USER,
        'PWD' : PWD,
        'SIGNATURE' : SIGNATURE,

        'returnUrl' : returnUrl,
        'cancelUrl' : cancelUrl,

        'PAYMENTREQUEST_0_PAYMENTACTION' : 'Sale',
        'L_PAYMENTREQUEST_0_NAME0' : 'Awesome Chocolates',
        'L_PAYMENTREQUEST_0_NUMBER0':'623083',
        'L_PAYMENTREQUEST_0_DESC0=Size' : '8.8-oz',
        'L_PAYMENTREQUEST_0_AMT0' : '9.95',
        'L_PAYMENTREQUEST_0_QTY0' : '2',
        'L_PAYMENTREQUEST_0_NAME1' : 'Bags of awesome sweets',
        'L_PAYMENTREQUEST_0_NUMBER1' : '623084',
        'L_PAYMENTREQUEST_0_DESC1' : 'Size: Two 24-piece boxes',
        'L_PAYMENTREQUEST_0_AMT1' : '39.70',
        'L_PAYMENTREQUEST_0_QTY1' : '2',
        'PAYMENTREQUEST_0_ITEMAMT' : '99.30',
        'PAYMENTREQUEST_0_TAXAMT' : '2.58',
        'PAYMENTREQUEST_0_SHIPPINGAMT' : '3.00',
        'PAYMENTREQUEST_0_HANDLINGAMT' : '2.99',
        'PAYMENTREQUEST_0_SHIPDISCAMT' : '-3.00',
        'PAYMENTREQUEST_0_INSURANCEAMT' : '1.00',
        'PAYMENTREQUEST_0_AMT' : '105.87',
        'PAYMENTREQUEST_0_CURRENCYCODE' : 'USD',
        'ALLOWNOTE' : '1',
    }


    #x` setExpressCheckout

    # sends the encoded request
    data = urllib.urlencode(values)
    req = urllib2.Request(API_SERVER, data)
    response = urllib2.urlopen(req)

    responseString = response.read()
    # parse the response
    token = parseToken(responseString)
    
    print 'setExpressCheckout token: ' + token
    # redirect the customer to paypal

    redirectUrl = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=" + token
    
    return redirect(redirectUrl)
    # return "buying stuff"


@app.route('/getCheckoutDetails')
def getCheckoutDetails():
    queryParameters = request.args
    # payerId = queryParameters.get('PayerID')

    values = {

        'METHOD' : 'GetExpressCheckoutDetails',
        'VERSION' : '109.0',
        
        'USER' : USER,
        'PWD' : PWD,
        'SIGNATURE' : SIGNATURE,
        'TOKEN' : queryParameters.get('token'),
    }

    data = urllib.urlencode(values)
    req = urllib2.Request(API_SERVER, data)
    response = urllib2.urlopen(req)

    responseString = response.read()
    print responseString

    return "gotcheckoutdetails"


@app.route('/success')
def success():
    
    # return render_template('payment_success.html', payerId=payerId)
    return render_template('payment_success.html')

@app.route('/cancel')
def cancel():

    return render_template('failure.html')
# helper function to get the token from the response string
def parseToken(inp):
    firstKey = ""

    equalSignOfTokenIndex = 0
    for i, v in enumerate(inp):
        firstKey+=v

        if "TOKEN=" in firstKey:
            equalSignOfTokenIndex = i
            break

    tokenString = ""
    for character in inp[equalSignOfTokenIndex+1:]:
        if character == "&":
            break

        tokenString += character

    return tokenString





