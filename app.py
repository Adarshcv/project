from flask import *
from datetime import datetime
from db import *
from functools import wraps
from flask_login import *
app=Flask(__name__)
app.secret_key="abc"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    qry = "SELECT * FROM \"user\" WHERE id = %s"
    val = (user_id,)
    user_data = selectone(qry, val)
    if user_data:
        user = User(id=user_data[0])
        return user
    return None
def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

        
        user_type = get_user_type(current_user.id)

        if user_type != 'admin':
            return '''<script>alert("YOU DONT HAVE PERMISSION TO ACCESS THIS PAGE LOGIN AGAIN");window.location='/logout'</script>'''
        return func(*args, **kwargs)
    return decorated_function

def get_user_type(user_id):
    query = "SELECT type FROM \"user\" WHERE id = %s"
    values = (user_id,)
    result=selectone(query, values)
    if result:
        return result[0]
    return None  # 

#main
#-------------------------------------------------------------------------
@app.route("/")
def main():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        return render_template("login.html")
#Authentication and registration
#--------------------------------------------------------------------------
def check_user_credentials(username, password):
    qry = "SELECT * FROM \"user\" WHERE username = %s AND password = %s;"
    val = (username, password)
    res = selectone(qry, val)
    return res

@app.route("/login", methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    res = check_user_credentials(username, password)

    if res is not None:
        id = str(res[0])
        user = User(id=id)
        login_user(user)  # Login the user using Flask-Login
        if res[-2] == 'admin':
            return redirect('/admindash1?id=' + id)
        else:
            return redirect('/home1?id=' + id)
    else:
        return redirect('/invalid')

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/regnow",methods=['post'])
def regnow():
    print(request.form)
    name=request.form['name']
    username=request.form['email']
    phone=request.form['phone']
    password=request.form['password']
    qry="INSERT INTO \"user\" (\"name\",\"username\",\"password\",\"type\",\"phone\") values(%s,%s,%s,'user',%s)"
    val=(name,username,password,phone)
    id=iud(qry,val)
    if id is not None:
        return '''<script>alert("REGISTRATION SUCCESS");window.location='/'</script>'''
    else:
        return '''<script>alert("invalid data please re-enter the data");window.location='/register'</script>'''
#----------------------------------------------------------------------------------------------------------------------





#ADMIN PAGES
#---------------------------------------------------------------------------------------------------------------------


@app.route("/admindash1")
@admin_required
def admindash1():
    try:
        id = request.args.get('id')
        session['uaid']=id
        qry = "SELECT * FROM \"user\" WHERE id = %s"
        val = (id,)
        res = selectone(qry, val)  
        return render_template("admin-dash.html", val=res)
    except:
        return redirect("/logout")
@app.route("/admindash")
@admin_required
def admindash():
    try:
        id = session.get('uaid')
        qry = "SELECT * FROM \"user\" WHERE id = %s"
        val = (id,)
        res = selectone(qry, val)  
        return render_template("admin-dash.html", val=res)
    except:
        return redirect("/logout")

@app.route("/adminmp")
@admin_required
def adminmp():
     try:
        qry="SELECT * FROM \"product\" "
        res= selectall(qry)
        return render_template("admin-mp.html", val=res)
     except:
        return redirect("/admindash")
@app.route("/add")
@admin_required
def add():
    return render_template("add.html")

@app.route("/addproduct", methods=['POST'])
@admin_required
def addproduct():
    try:
        name = request.form['name']
        desc = request.form['desc']
        price = float(request.form['price'])  # Convert to float
        stock = int(request.form['stock'])    # Convert to integer
        img = request.files['file']
        if img:
            fn = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"
            img.save("static/images/" + fn)
            val = (name, desc, price, stock, fn)
            qry = "INSERT INTO \"product\"(p_name, description, price, stock, img) VALUES (%s, %s, %s, %s, %s)"
            iud(qry, val)
        return redirect("/adminmp")
    except:
        return redirect("/admindash")

@app.route("/deleteproduct",)
@admin_required
def deleteproduct():
    try:
        id=request.args.get("p_id")
        qry = "DELETE FROM \"cartitem\" where \"p_id\"=%s"
        x=dell(qry,id)
        qry1 = "DELETE FROM \"product\" where \"p_id\"=%s"
        y=dell(qry1,id)
        return redirect("/adminmp")
    except:
        return redirect("/admindash")
    
@app.route("/adminor")
@admin_required
def adminor():
    qry="SELECT * FROM \"order\""
    res= selectall(qry)
    return render_template("admin-or.html", val=res)
@app.route("/ordered")
@admin_required
def ordered():
    orderid=request.args.get("orderid")
    val=(orderid,)
    qry = "UPDATE \"order\" SET status='ordered' WHERE order_id=%s"
    x=update(qry,val)
    return redirect("/adminor")
@app.route("/shipped")
@admin_required
def shipped():
    orderid=request.args.get("orderid")
    val=(orderid,)
    qry = "UPDATE \"order\" SET status='shipped' WHERE order_id=%s"
    x=update(qry,val)
    return redirect("/adminor")
@app.route("/delivered")
@admin_required
def delivered():
    orderid=request.args.get("orderid")
    val=(orderid,)
    qry = "UPDATE \"order\" SET status='delivered' WHERE order_id=%s"
    x=update(qry,val)
    return redirect("/adminor")
@app.route("/avieworder")
@admin_required
def avieworder():
    orderid=request.args.get("orderid")
    val=(orderid,)
    qry3= "SELECT * FROM \"order\" WHERE order_id=%s"
    z=selectone(qry3,val)
    uid=z[1]
    vall=(uid,)
    qry3= "SELECT * FROM \"user\" WHERE id=%s"
    w=selectone(qry3,vall)
    qry = "SELECT * FROM \"orderitem\" WHERE order_id=%s"
    x=selectall2(qry,val)
    plist=[]
    for product in x:
        productid=product[2]
        val2=(productid,)
        qry2= "SELECT * FROM \"product\" WHERE p_id=%s"
        y=selectall2(qry2,val2)
        plist.append(y)
    print(plist)
    return render_template("avieworder.html",res=x,res2=plist,res1=z,res3=w)
    
#---------------------------------------------------------------------------------------------------------------------



#USERPAGES
#---------------------------------------------------------------------------------------------------
@app.route("/home1")
@login_required
def home1():
    try:
        id = request.args.get('id')
        session['uuid']=id
        qry1 = "SELECT * FROM \"user\" WHERE id = %s"
        val1 = (id,)
        res1 = selectone(qry1, val1)
        qry="SELECT * FROM product"
        res=selectall(qry)
        return render_template("home.html",val=res,val1=res1)
    except:
        return redirect("/")
@app.route("/home")
@login_required
def home():
    try:
        id = session.get('id')
        qry1 = "SELECT * FROM \"user\" WHERE id = %s"
        val1 = (id,)
        res1 = selectone(qry1, val1)
        qry="SELECT * FROM product"
        res=selectall(qry)
        return render_template("home.html",val=res,val1=res1)
    except:
        return redirect("/")
# @app.route("/search",methods=['POST'])
# def search():
#     try:
#         key = request.args.get('key')
#         id=session.get('uuid')
#         val=(key,)
#         qry1 = "SELECT * FROM \"product\" WHERE name ILIKE %s"
#         res1 = selectall2(qry,val)
#         return render_template("home.html?{{id}}",val=res1)
#     except:
#         return redirect("/")

@app.route("/add_to_cart")
@login_required
def add_to_cart():
    try:
        product_id = request.args.get('product_id')
        user_id = session.get('uuid')
        print("pid"+product_id)
        print("userid"+user_id)
        val=(user_id,)
        qry="INSERT INTO \"cart\" (u_id) values(%s) ON CONFLICT (u_id) DO NOTHING RETURNING cart_id";
        cart_i=iud(qry,val)
        val2=(user_id,)
        qry2="Select \"cart_id\" FROM \"cart\" WHERE u_id=%s"
        cart_id=selectone(qry2,val2)
        print(cart_id)
        c_id=str(cart_id[0])
        session['cartiid']=cart_id
        print(cart_id)
        val1=(cart_id,product_id)
        qry1="INSERT INTO \"cartitem\" (cart_id,p_id,quantity) values(%s,%s,1) ON CONFLICT (cart_id,p_id) DO NOTHING RETURNING p_id"
        res=iud(qry1,val1)
        return redirect("/cart")
    except:
        return redirect("/home")
@app.route('/cart')
@login_required
def cart():
    try:
        tot=0
        cartid = session.get('cartiid')
        print(cartid)
        qry = "SELECT * FROM \"cartitem\" WHERE \"cart_id\"=%s"
        cart=selectall2(qry,cartid)
        pids = [product[2] for product in cart]
        pval = ','.join(['%s'] * len(pids))
        if pids:
            qry1 = "SELECT * FROM \"product\" WHERE p_id IN ({})".format(pval)
            cart1 = selectall2(qry1,pids)
        else:
            cart1=[]
        for product in cart1:
            tot=tot+product[3]
        session['total']=tot
        return render_template('cart.html',cart_items=cart,cart_product=cart1,cartid1=cartid)
    except:
        return redirect("/home")
@app.route("/deletecart",)
@login_required
def deletecart():
    try:
        id=request.args.get("p_id")
        qry = "DELETE FROM \"cartitem\" where \"p_id\"=%s"
        x=dell(qry,id)
        return redirect("/cart")
    except:
        return redirect("/")
@app.route("/clearcart",)
@login_required
def clearcart():
    try:
        id=request.args.get("cart_id")
        print(id)
        val=(id,)
        qry = "DELETE FROM \"cartitem\" where \"cart_id\"=%s"
        x=dell(qry,val)
        return redirect("/cart")
    except:
        return redirect("/home")

#----------------------------------------------------------------------------------


@app.route("/add_to_fav")
@login_required
def add_to_fav():
    try:
        product_id = request.args.get('product_id')
        user_id = session.get('uuid')
        print("pid"+product_id)
        print("userid"+user_id)
        val=(user_id,)
        qry="INSERT INTO \"fav\" (u_id) values(%s) ON CONFLICT (u_id) DO NOTHING RETURNING fav_id";
        fav_i=iud(qry,val)
        val2=(user_id,)
        qry2="Select \"fav_id\" FROM \"fav\" WHERE u_id=%s"
        fav_id=selectone(qry2,val2)
        print(fav_id)
        c_id=str(fav_id[0])
        session['faviid']=fav_id
        session['uuid']=user_id
        print(fav_id)
        val1=(fav_id,product_id)
        qry1="INSERT INTO \"favitems\" (fav_id,p_id) values(%s,%s) ON CONFLICT (fav_id,p_id) DO NOTHING RETURNING p_id"
        res=iud(qry1,val1)
        return redirect("/fav")
    except:
        return redirect("/home")
@app.route('/fav')
@login_required
def fav():
    try:
        favid = session.get('faviid')
        userid = session.get('uuid')
        print(favid)
        qry = "SELECT * FROM \"favitems\" WHERE \"fav_id\"=%s"
        fav=selectall2(qry,favid)
        pids = [product[2] for product in fav]
        pval = ','.join(['%s'] * len(pids))
        if pids:
            qry1 = "SELECT * FROM \"product\" WHERE p_id IN ({})".format(pval)
            fav1 = selectall2(qry1,pids)
        else:
            fav1=[]
        return render_template('fav.html',fav_items=fav,fav_product=fav1,favid1=favid)
    except:
        return redirect("/home")
@app.route("/deletefav")
@login_required
def deletefav():
    try:
        id=request.args.get("p_id")
        qry = "DELETE FROM \"favitems\" where \"p_id\"=%s"
        x=dell(qry,id)
        return redirect("/fav")
    except:
        return redirect("/home")
@app.route("/clearfav",)
@login_required
def clearfav():
    try:
        id=request.args.get("fav_id")
        print(id)
        val=(id,)
        qry = "DELETE FROM \"favitems\" where \"fav_id\"=%s"
        x=dell(qry,val)
        return redirect("/fav")
    except:
        return redirect("/home")

@app.route("/favtocart")
@login_required
def favtocart():
    try:
        product_id = request.args.get('product_id')
        user_id = session.get('uuid')
        val=(user_id,)
        qry="INSERT INTO \"cart\" (u_id) values(%s) ON CONFLICT (u_id) DO NOTHING RETURNING cart_id";
        cart_i=iud(qry,val)
        val2=(user_id,)
        qry2="Select \"cart_id\" FROM \"cart\" WHERE u_id=%s"
        cart_id=selectone(qry2,val2)
        print(cart_id)
        c_id=str(cart_id[0])
        session['cartiid']=cart_id
        print(cart_id)
        val1=(cart_id,product_id)
        qry1="INSERT INTO \"cartitem\" (cart_id,p_id,quantity) values(%s,%s,1) ON CONFLICT (cart_id,p_id) DO NOTHING RETURNING p_id"
        res=iud(qry1,val1)
        return redirect("/cart")
    except:
        return redirect("/home")

@app.route("/alltocart")
@login_required
def alltocart():
    try:
        favid = request.args.get('fav_id')
        value = (favid,)
        qry = "SELECT p_id FROM \"favitems\" WHERE fav_id=%s"
        pp = selectall2(qry,value)
        user_id = session.get('uuid')
        val=(user_id,)
        qry="INSERT INTO \"cart\" (u_id) values(%s) ON CONFLICT (u_id) DO NOTHING RETURNING cart_id";
        cart_i=iud(qry,val)
        val2=(user_id,)
        qry2="Select \"cart_id\" FROM \"cart\" WHERE u_id=%s"
        cart_id=selectone(qry2,val2)
        print(cart_id)
        c_id=str(cart_id[0])
        session['cartiid']=cart_id
        print(cart_id)
        for pps in pp:
            print(pps)
            val1=(cart_id,pps)
            qry1="INSERT INTO \"cartitem\" (cart_id,p_id,quantity) values(%s,%s,1)ON CONFLICT (cart_id,p_id) DO NOTHING RETURNING p_id"
            res=iud(qry1,val1)
        return redirect("/cart")
    except:
        return redirect("/home")
#------------------------------------------------------------------------------------------------------------
@app.route("/checkout")
@login_required
def checkout():
    try:
        uid = session.get('uuid')
        value = (uid,)
        qry = "SELECT * FROM \"user\" WHERE id = %s"
        uu = selectone(qry,value)
        total=session.get('total')
        print(uu)
        return render_template("/checkout.html",tot=total,us=uu)
    except:
        return redirect("/home")

@app.route("/address")
@login_required
def address():
    try:
        uid = session.get('uuid')
        value = (uid,)
        qry = "SELECT * FROM \"user\" WHERE id = %s"
        uu = selectone(qry,value)
        total=session.get('total')
        print(uu)
        return render_template("/checkout.html",tot=total,us=uu)
    except:
        return redirect("/home")
@app.route("/addtoorder",methods=['POST'])
@login_required
def addtoorder():
    # try:
    uid = session.get('uuid')
    value = (uid,)
    qry1 = "SELECT * FROM \"user\" WHERE id = %s"
    uu = selectone(qry1,value)
    print(uu)
    total=session.get('total')
    name = uu[1]
    house = request.form['house']
    street = request.form['street']
    area = request.form['area']
    address =[ name+" , "+house+" , "+street+" , "+area ]
    val=(uid,total,'ordered',address,)
    qry="INSERT INTO \"order\" (u_id,total,status,address) VALUES(%s,%s,%s,%s) "
    res=iud(qry,val)
    orderid=res
    cartid=session['cartiid']
    val1 = (cartid,)
    qry2 = "SELECT p_id FROM \"cartitem\" WHERE cart_id=%s"
    pp = selectall2(qry2,val1)
    for pps in pp:
        qr="SELECT price FROM \"product\" where p_id=%s"
        va=(pps,)
        price=selectone(qr,va)
        val1=(orderid,pps,'1',price)
        qry1="INSERT INTO \"orderitem\" (order_id,p_id,quantity,unit_price) values(%s,%s,%s,%s) ON CONFLICT (order_id,p_id) DO NOTHING RETURNING p_id"
        res=iud(qry1,val1)
        qry2="UPDATE \"product\" SET stock=stock - 1 where p_id=%s"
        ress=update(qry2,va)
    oi=str(orderid)
    return redirect('/order?orderid='+ oi)
    # except:\

@app.route("/order")
@login_required
def order():
    orderid = request.args.get('orderid')
    val=(orderid,)
    qry="SELECT * FROM \"order\" WHERE order_id=%s"
    res=selectone(qry,val,)
    userid=res[1]
    val1=(userid,)
    qry1="SELECT * FROM \"user\" WHERE id=%s"
    res1=selectone(qry1,val1)
    print(res1)
    cartid=session.get('cartiid')
    val2=(cartid,)
    qry2="DELETE FROM \"cartitem\" WHERE cart_id=%s"
    res2=dell(qry2,val2)
    print(res2)
    qry3="DELETE FROM \"cart\" WHERE cart_id=%s"
    res3=dell(qry3,val2)
    print(qry3)
    qry1="SELECT * FROM \"user\" WHERE id=%s"
    res1=selectone(qry1,val1)
    print(res1)
    return render_template("order.html",res=res,ress=res1,)

@app.route("/vieworder")
@login_required
def vieworder():
    orderid=request.args.get("orderid")
    val=(orderid,)
    qry3= "SELECT * FROM \"order\" WHERE order_id=%s"
    z=selectone(qry3,val)
    uid=z[1]
    vall=(uid,)
    qry3= "SELECT * FROM \"user\" WHERE id=%s"
    w=selectone(qry3,vall)
    qry = "SELECT * FROM \"orderitem\" WHERE order_id=%s"
    x=selectall2(qry,val)
    plist=[]
    for product in x:
        productid=product[2]
        val2=(productid,)
        qry2= "SELECT * FROM \"product\" WHERE p_id=%s"
        y=selectall2(qry2,val2)
        plist.append(y)
    print(plist)
    return render_template("vieworder.html",res=x,res2=plist,res1=z,res3=w)

@app.route("/profile")
@login_required
def profile():
    id=session.get('uuid')
    val1=(id,)
    qry1="SELECT * FROM \"user\" WHERE id=%s"
    x=selectone(qry1,val1)
    return render_template("profile.html",res=x,)
@app.route("/orderr")
@login_required
def orderr():
    try:

        id=session.get('uuid')
        val1=(id,)
        qry1="SELECT order_id from \"order\" WHERE u_id=%s"
        x=selectone(qry1,val1)
        orderid=x
        val=(orderid,)
        qry="SELECT * FROM \"order\" WHERE order_id=%s"
        y= selectall2(qry,val)
        return render_template("user-or.html", val=y,val1=x)
    except:
        return redirect("/")
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect("/")
app.run(debug=True)
#-----------------------------------------------------------------------------------------------------------------------------------
