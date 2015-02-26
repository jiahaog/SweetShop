from flask import render_template, request, redirect, url_for
from app import app
import urllib
import urllib2
import urlparse
from helper import getFromResponseWithKey, getAddressFromResponse
from config import ROOT_URL, USER, PWD, SIGNATURE, API_SERVER


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

    # sends the encoded request
    data = urllib.urlencode(values)
    req = urllib2.Request(API_SERVER, data)
    response = urllib2.urlopen(req)
    responseString = response.read()

    # parse the response
    token = getFromResponseWithKey(responseString, 'TOKEN')
    
    # redirect the customer to paypal
    redirectUrl = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=" + token
    
    return redirect(redirectUrl)


@app.route('/getCheckoutDetails')
def getCheckoutDetails():
    queryParameters = request.args
    
    token = queryParameters.get('token')
    

    values = {

        'METHOD' : 'GetExpressCheckoutDetails',
        'VERSION' : '109.0',
        
        'USER' : USER,
        'PWD' : PWD,
        'SIGNATURE' : SIGNATURE,
        'TOKEN' : token,
    }

    data = urllib.urlencode(values)
    req = urllib2.Request(API_SERVER, data)
    response = urllib2.urlopen(req)

    responseString = response.read()

    email = getFromResponseWithKey(responseString, 'EMAIL')
    payerId = getFromResponseWithKey(responseString, 'PAYERID')
    totalAmt = getFromResponseWithKey(responseString, 'AMT')
    address = getAddressFromResponse(responseString)
    print address

    # Passes the token and payerid to the confirm link, which will 
    # be passed to the success() function

    doCheckoutParameters = '?token=' + token + '&PayerID=' + payerId

    return render_template('confirm.html', payerId=payerId, email=email, totalAmt=totalAmt, address=address, queryParameters=doCheckoutParameters)


@app.route('/success')
def success():
    
    queryParameters = request.args
    token = queryParameters.get('token')
    payerId = queryParameters.get('PayerID')
    values = {

        'METHOD' : 'DoExpressCheckoutPayment',
        'VERSION' : '109.0',
        
        'USER' : USER,
        'PWD' : PWD,
        'SIGNATURE' : SIGNATURE,
        'TOKEN' : token,

        'PAYERID' : payerId,

        'PAYMENTREQUEST_0_AMT' : '105.87',
        'PAYMENTREQUEST_0_CURRENCYCODE' : 'USD',
        'PAYMENTREQUEST_0_PAYMENTACTION' : 'Sale',
    }


    data = urllib.urlencode(values)
    req = urllib2.Request(API_SERVER, data)
    response = urllib2.urlopen(req)

    responseString = response.read()
    

    success = getFromResponseWithKey(responseString, 'PAYMENTINFO_0_ACK')


    if (success == 'Success'):
        return render_template('payment_success.html')

    else:
        return redirect(url_for('cancel'))


@app.route('/cancel')
def cancel():

    return render_template('failure.html')
